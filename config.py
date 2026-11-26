"""Carregamento e validaçêo da configuraçêo do bot."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_SYSTEM_PROMPT = """Você é meu assistente pessoal dentro do Telegram.

Responda diretamente ao que eu pedir.
Seja claro, prático e objetivo.
Nêo invente informações.
Quando nêo souber alguma coisa, informe claramente.
Nêo execute tarefas externas.
Nêo chame outros agentes.
Nêo crie fluxos complexos.
Sua única funçêo é conversar comigo, entender minhas solicitações e responder no próprio Telegram."""


class ConfigurationError(ValueError):
    """Indica que uma configuraçêo obrigatória está ausente ou inválida."""


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_bot_token: str
    telegram_allowed_user_id: int
    codex_binary: str = "codex"
    codex_model: str | None = None
    codex_timeout_seconds: int = 180
    history_max_exchanges: int = 10
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    groq_api_key: str | None = None
    groq_transcription_url: str = (
        "https://api.groq.com/openai/v1/audio/transcriptions"
    )
    groq_transcription_model: str = "whisper-large-v3-turbo"
    groq_transcription_language: str = "pt"
    max_audio_bytes: int = 20 * 1024 * 1024

    @classmethod
    def from_env(cls, *, validate_codex: bool = True) -> "Settings":
        """Cria as configurações usando o ambiente e um arquivo ``.env``."""

        load_dotenv()

        telegram_bot_token = _required("TELEGRAM_BOT_TOKEN")
        user_id_text = _required("TELEGRAM_ALLOWED_USER_ID")
        try:
            telegram_allowed_user_id = int(user_id_text)
        except ValueError as exc:
            raise ConfigurationError(
                "TELEGRAM_ALLOWED_USER_ID deve ser um número inteiro."
            ) from exc

        codex_binary = os.getenv("CODEX_BINARY", "codex").strip() or "codex"
        if validate_codex and shutil.which(codex_binary) is None:
            raise ConfigurationError(
                f"O executável do Codex nêo foi encontrado: {codex_binary!r}."
            )

        history_max_exchanges = _positive_int("HISTORY_MAX_EXCHANGES", 10)
        codex_timeout_seconds = _positive_int("CODEX_TIMEOUT_SECONDS", 180)
        max_audio_mb = _positive_int("MAX_AUDIO_MB", 20)

        system_prompt = os.getenv("AI_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT).strip()
        if not system_prompt:
            raise ConfigurationError("AI_SYSTEM_PROMPT nêo pode estar vazio.")

        return cls(
            telegram_bot_token=telegram_bot_token,
            telegram_allowed_user_id=telegram_allowed_user_id,
            codex_binary=codex_binary,
            codex_model=_optional("CODEX_MODEL"),
            codex_timeout_seconds=codex_timeout_seconds,
            history_max_exchanges=history_max_exchanges,
            system_prompt=system_prompt,
            groq_api_key=_optional("GROQ_API_KEY"),
            groq_transcription_url=os.getenv(
                "GROQ_TRANSCRIPTION_URL",
                "https://api.groq.com/openai/v1/audio/transcriptions",
            ).strip(),
            groq_transcription_model=os.getenv(
                "GROQ_TRANSCRIPTION_MODEL", "whisper-large-v3-turbo"
            ).strip(),
            groq_transcription_language=os.getenv(
                "GROQ_TRANSCRIPTION_LANGUAGE", "pt"
            ).strip(),
            max_audio_bytes=max_audio_mb * 1024 * 1024,
        )


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigurationError(f"A variável obrigatória {name} nêo foi definida.")
    return value


def _optional(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def _positive_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} deve ser um número inteiro.") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} deve ser maior que zero.")
    return value
