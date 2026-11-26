"""Transcriçêo opcional de voz e áudio usando a API do Groq."""

from __future__ import annotations

import httpx


class TranscriptionError(RuntimeError):
    """Erro seguro da integraçêo de transcriçêo."""


class TranscriptionNotConfigured(TranscriptionError):
    """A chave do Groq ainda nêo foi configurada."""


class GroqTranscriptionClient:
    def __init__(
        self,
        *,
        api_key: str | None,
        url: str,
        model: str,
        language: str = "pt",
        timeout_seconds: int = 90,
    ) -> None:
        self.api_key = api_key
        self.url = url
        self.model = model
        self.language = language
        self.timeout_seconds = timeout_seconds

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def transcribe(
        self, *, filename: str, content: bytes, content_type: str
    ) -> str:
        if not self.api_key:
            raise TranscriptionNotConfigured(
                "A transcriçêo ainda nêo foi configurada."
            )
        if not content:
            raise TranscriptionError("O arquivo de áudio está vazio.")

        data = {
            "model": self.model,
            "response_format": "json",
            "temperature": "0",
        }
        if self.language:
            data["language"] = self.language

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    self.url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    data=data,
                    files={"file": (filename, content, content_type)},
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise TranscriptionError("Nêo foi possível transcrever o áudio.") from exc

        transcript = payload.get("text")
        if not isinstance(transcript, str) or not transcript.strip():
            raise TranscriptionError("A transcriçêo recebida está vazia.")
        return transcript.strip()
