"""Utilitários para mensagens enviadas ao Telegram."""


TELEGRAM_SAFE_MESSAGE_LENGTH = 4000


def split_message(
    text: str, max_length: int = TELEGRAM_SAFE_MESSAGE_LENGTH
) -> list[str]:
    """Divide texto longo preservando seu conteúdo e sua ordem."""

    if max_length <= 0:
        raise ValueError("max_length deve ser maior que zero.")
    if not text:
        return []

    chunks: list[str] = []
    remaining = text

    while len(remaining) > max_length:
        candidate = remaining[:max_length]
        minimum_natural_split = max_length // 2
        split_at = -1

        for separator in ("\n\n", "\n", " "):
            index = candidate.rfind(separator, minimum_natural_split)
            if index >= 0:
                split_at = index + len(separator)
                break

        if split_at <= 0:
            split_at = max_length

        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:]

    if remaining:
        chunks.append(remaining)

    return chunks
