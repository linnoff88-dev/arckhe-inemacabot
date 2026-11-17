import os
import unittest
from unittest.mock import patch

from config import ConfigurationError, Settings


BASE_ENV = {
    "TELEGRAM_BOT_TOKEN": "token-de-teste",
    "TELEGRAM_ALLOWED_USER_ID": "123456",
}


class SettingsTests(unittest.TestCase):
    def test_loads_minimum_valid_configuration(self) -> None:
        with patch.dict(os.environ, BASE_ENV, clear=True):
            settings = Settings.from_env(validate_codex=False)
        self.assertEqual(settings.telegram_allowed_user_id, 123456)
        self.assertEqual(settings.history_max_exchanges, 10)
        self.assertIsNone(settings.groq_api_key)

    def test_rejects_missing_token(self) -> None:
        with patch.dict(
            os.environ, {"TELEGRAM_ALLOWED_USER_ID": "123"}, clear=True
        ):
            with self.assertRaises(ConfigurationError):
                Settings.from_env(validate_codex=False)

    def test_rejects_non_numeric_user_id(self) -> None:
        env = {**BASE_ENV, "TELEGRAM_ALLOWED_USER_ID": "não-é-número"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_env(validate_codex=False)

    def test_rejects_invalid_history_limit(self) -> None:
        env = {**BASE_ENV, "HISTORY_MAX_EXCHANGES": "0"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_env(validate_codex=False)


if __name__ == "__main__":
    unittest.main()
