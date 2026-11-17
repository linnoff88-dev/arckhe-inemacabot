import unittest

from codex_client import CodexClient
from history import Message


class CodexClientTests(unittest.TestCase):
    def test_prompt_contains_instruction_history_and_current_message(self) -> None:
        client = CodexClient(binary="codex", system_prompt="Seja direto.")
        prompt = client._build_prompt(
            [
                Message(role="user", content="Pergunta anterior"),
                Message(role="assistant", content="Resposta anterior"),
            ],
            "Pergunta atual",
        )

        self.assertIn("Seja direto.", prompt)
        self.assertIn("Usuário: Pergunta anterior", prompt)
        self.assertIn("Assistente: Resposta anterior", prompt)
        self.assertIn("Pergunta atual", prompt)
        self.assertIn("Não use ferramentas", prompt)


if __name__ == "__main__":
    unittest.main()
