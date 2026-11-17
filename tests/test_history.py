import unittest

from history import ConversationHistory


class ConversationHistoryTests(unittest.TestCase):
    def test_keeps_only_configured_number_of_exchanges(self) -> None:
        history = ConversationHistory(max_exchanges=2)
        history.add_exchange("um", "resposta um")
        history.add_exchange("dois", "resposta dois")
        history.add_exchange("três", "resposta três")

        messages = history.snapshot()
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0].content, "dois")
        self.assertEqual(messages[-1].content, "resposta três")

    def test_clear_removes_every_message(self) -> None:
        history = ConversationHistory()
        history.add_exchange("pergunta", "resposta")
        history.clear()
        self.assertEqual(history.snapshot(), ())

    def test_rejects_invalid_limit(self) -> None:
        with self.assertRaises(ValueError):
            ConversationHistory(max_exchanges=0)


if __name__ == "__main__":
    unittest.main()
