import unittest

from message_utils import split_message


class SplitMessageTests(unittest.TestCase):
    def test_returns_short_message_unchanged(self) -> None:
        self.assertEqual(split_message("olá", max_length=10), ["olá"])

    def test_splits_and_preserves_all_content(self) -> None:
        text = ("primeiro parágrafo\n\n" * 8) + ("x" * 25)
        chunks = split_message(text, max_length=30)

        self.assertEqual("".join(chunks), text)
        self.assertTrue(all(0 < len(chunk) <= 30 for chunk in chunks))

    def test_hard_splits_long_word(self) -> None:
        chunks = split_message("a" * 21, max_length=10)
        self.assertEqual([len(chunk) for chunk in chunks], [10, 10, 1])

    def test_empty_text_produces_no_messages(self) -> None:
        self.assertEqual(split_message(""), [])


if __name__ == "__main__":
    unittest.main()
