"""Cliente de conversa baseado no Codex CLI autenticado localmente."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Sequence

from history import Message


class CodexError(RuntimeError):
    """Erro seguro e apresentável da integração com o Codex."""


class CodexClient:
    def __init__(
        self,
        *,
        binary: str,
        system_prompt: str,
        model: str | None = None,
        timeout_seconds: int = 180,
    ) -> None:
        self.binary = binary
        self.system_prompt = system_prompt
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def answer(self, history: Sequence[Message], user_message: str) -> str:
        """Executa uma sessão efêmera e devolve somente a resposta final."""

        prompt = self._build_prompt(history, user_message)

        with tempfile.TemporaryDirectory(prefix="inemacabot-codex-") as temp_dir:
            output_path = Path(temp_dir) / "answer.txt"
            command = [
                self.binary,
                "exec",
                "--skip-git-repo-check",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--sandbox",
                "read-only",
                "--color",
                "never",
                "--cd",
                temp_dir,
                "--output-last-message",
                str(output_path),
            ]
            if self.model:
                command.extend(["--model", self.model])
            command.append("-")

            try:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE,
                )
                _, stderr = await asyncio.wait_for(
                    process.communicate(prompt.encode("utf-8")),
                    timeout=self.timeout_seconds,
                )
            except TimeoutError as exc:
                if "process" in locals() and process.returncode is None:
                    process.kill()
                    await process.wait()
                raise CodexError("O Codex demorou demais para responder.") from exc
            except OSError as exc:
                raise CodexError("Não foi possível iniciar o Codex CLI.") from exc

            if process.returncode != 0:
                detail = stderr.decode("utf-8", errors="replace").strip()
                if len(detail) > 500:
                    detail = detail[-500:]
                raise CodexError(
                    f"O Codex terminou com erro ({process.returncode}): {detail}"
                )

            try:
                answer = output_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                raise CodexError("O Codex não produziu uma resposta legível.") from exc

        if not answer:
            raise CodexError("O Codex devolveu uma resposta vazia.")
        return answer

    def _build_prompt(
        self, history: Sequence[Message], user_message: str
    ) -> str:
        lines = [
            "<system_instruction>",
            self.system_prompt,
            "</system_instruction>",
            "",
            "Responda somente com a mensagem final destinada ao usuário.",
            "Não use ferramentas, não execute comandos e não acesse arquivos.",
            "",
            "<conversation_history>",
        ]

        for message in history:
            label = "Usuário" if message.role == "user" else "Assistente"
            lines.append(f"{label}: {message.content}")

        lines.extend(
            [
                "</conversation_history>",
                "",
                "<current_user_message>",
                user_message,
                "</current_user_message>",
            ]
        )
        return "\n".join(lines)
