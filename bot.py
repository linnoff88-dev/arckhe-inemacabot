"""Ponto de entrada do assistente pessoal no Telegram."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from telegram import BotCommand, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from auth import is_authorized
from codex_client import CodexClient, CodexError
from config import ConfigurationError, Settings
from history import ConversationHistory
from message_utils import split_message
from transcription_client import (
    GroqTranscriptionClient,
    TranscriptionError,
    TranscriptionNotConfigured,
)


LOGGER = logging.getLogger(__name__)
START_MESSAGE = "Olá! Sou seu assistente pessoal. Envie uma mensagem e eu responderei."
HELP_MESSAGE = (
    "Envie uma mensagem de texto, uma mensagem de voz ou um arquivo de áudio. "
    "Use /limpar para apagar o contexto recente da conversa."
)
GENERIC_ERROR_MESSAGE = (
    "Não consegui responder agora. Tente novamente em alguns instantes."
)


@dataclass(slots=True)
class BotServices:
    settings: Settings
    history: ConversationHistory
    codex: CodexClient
    transcription: GroqTranscriptionClient
    conversation_lock: asyncio.Lock


def _services(context: ContextTypes.DEFAULT_TYPE) -> BotServices:
    return context.application.bot_data["services"]


def _authorized(update: Update, services: BotServices) -> bool:
    user = update.effective_user
    return is_authorized(
        user.id if user is not None else None,
        services.settings.telegram_allowed_user_id,
    )


async def start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    services = _services(context)
    if not _authorized(update, services) or update.effective_message is None:
        return
    await update.effective_message.reply_text(START_MESSAGE)


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    services = _services(context)
    if not _authorized(update, services) or update.effective_message is None:
        return
    await update.effective_message.reply_text(HELP_MESSAGE)


async def clear_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    services = _services(context)
    if not _authorized(update, services) or update.effective_message is None:
        return
    async with services.conversation_lock:
        services.history.clear()
    await update.effective_message.reply_text("Histórico da conversa apagado.")


async def text_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    services = _services(context)
    message = update.effective_message
    if not _authorized(update, services) or message is None or not message.text:
        return
    await _generate_and_reply(update, context, message.text.strip())


async def audio_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    services = _services(context)
    message = update.effective_message
    if not _authorized(update, services) or message is None:
        return

    media = message.voice or message.audio
    if media is None:
        return
    if not services.transcription.configured:
        await message.reply_text(
            "A transcrição de áudio ainda não está configurada. "
            "Defina GROQ_API_KEY no arquivo .env."
        )
        return
    if media.file_size and media.file_size > services.settings.max_audio_bytes:
        max_mb = services.settings.max_audio_bytes // (1024 * 1024)
        await message.reply_text(
            f"O áudio ultrapassa o limite configurado de {max_mb} MB."
        )
        return

    await context.bot.send_chat_action(
        chat_id=message.chat_id, action=ChatAction.TYPING
    )

    try:
        telegram_file = await context.bot.get_file(media.file_id)
        content = bytes(await telegram_file.download_as_bytearray())
        filename = getattr(media, "file_name", None) or "mensagem-de-voz.ogg"
        content_type = getattr(media, "mime_type", None) or "audio/ogg"
        transcript = await services.transcription.transcribe(
            filename=filename,
            content=content,
            content_type=content_type,
        )
    except TranscriptionNotConfigured:
        await message.reply_text(
            "A transcrição de áudio ainda não está configurada."
        )
        return
    except TranscriptionError:
        LOGGER.exception("Falha ao transcrever áudio do Telegram.")
        await message.reply_text(
            "Não consegui transcrever esse áudio. Tente novamente."
        )
        return
    except Exception:
        LOGGER.exception("Falha ao baixar áudio do Telegram.")
        await message.reply_text("Não consegui baixar esse áudio.")
        return

    await _generate_and_reply(update, context, transcript)


async def _generate_and_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_message: str,
) -> None:
    services = _services(context)
    message = update.effective_message
    if message is None or not user_message:
        return

    await context.bot.send_chat_action(
        chat_id=message.chat_id, action=ChatAction.TYPING
    )

    try:
        async with services.conversation_lock:
            answer = await services.codex.answer(
                services.history.snapshot(), user_message
            )
            services.history.add_exchange(user_message, answer)
    except CodexError:
        LOGGER.exception("Falha ao gerar resposta com o Codex.")
        await message.reply_text(GENERIC_ERROR_MESSAGE)
        return

    for chunk in split_message(answer):
        await message.reply_text(chunk)


async def error_handler(
    update: object, context: ContextTypes.DEFAULT_TYPE
) -> None:
    LOGGER.error(
        "Erro não tratado no bot: %s",
        type(context.error).__name__ if context.error else "desconhecido",
        exc_info=context.error,
    )


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Iniciar o assistente"),
            BotCommand("limpar", "Apagar o histórico da conversa"),
            BotCommand("ajuda", "Mostrar como usar o bot"),
        ]
    )


def build_application(settings: Settings) -> Application:
    services = BotServices(
        settings=settings,
        history=ConversationHistory(settings.history_max_exchanges),
        codex=CodexClient(
            binary=settings.codex_binary,
            model=settings.codex_model,
            system_prompt=settings.system_prompt,
            timeout_seconds=settings.codex_timeout_seconds,
        ),
        transcription=GroqTranscriptionClient(
            api_key=settings.groq_api_key,
            url=settings.groq_transcription_url,
            model=settings.groq_transcription_model,
            language=settings.groq_transcription_language,
        ),
        conversation_lock=asyncio.Lock(),
    )

    application = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_init(post_init)
        .build()
    )
    application.bot_data["services"] = services
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("limpar", clear_command))
    application.add_handler(CommandHandler("ajuda", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message)
    )
    application.add_handler(
        MessageHandler(filters.VOICE | filters.AUDIO, audio_message)
    )
    application.add_error_handler(error_handler)
    return application


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        raise SystemExit(f"Erro de configuração: {exc}") from exc

    LOGGER.info("Iniciando o bot por long polling.")
    build_application(settings).run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
