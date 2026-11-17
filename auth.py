"""Regras pequenas de autorização, separadas para facilitar os testes."""


def is_authorized(user_id: int | None, allowed_user_id: int) -> bool:
    """Retorna verdadeiro somente para o ID explicitamente autorizado."""

    return user_id is not None and user_id == allowed_user_id
