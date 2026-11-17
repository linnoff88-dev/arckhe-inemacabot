"""Histórico curto e não persistente da conversa."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Message:
    role: str
    content: str


class ConversationHistory:
    """Mantém os últimos pares usuário/assistente em memória."""

    def __init__(self, max_exchanges: int = 10) -> None:
        if max_exchanges <= 0:
            raise ValueError("max_exchanges deve ser maior que zero.")
        self._messages: deque[Message] = deque(maxlen=max_exchanges * 2)

    def add_exchange(self, user_message: str, assistant_message: str) -> None:
        self._messages.append(Message(role="user", content=user_message))
        self._messages.append(Message(role="assistant", content=assistant_message))

    def snapshot(self) -> tuple[Message, ...]:
        return tuple(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)
