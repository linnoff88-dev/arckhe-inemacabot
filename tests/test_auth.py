import unittest

from auth import is_authorized


class AuthorizationTests(unittest.TestCase):
    def test_accepts_only_allowed_user(self) -> None:
        self.assertTrue(is_authorized(123, 123))
        self.assertFalse(is_authorized(456, 123))
        self.assertFalse(is_authorized(None, 123))


if __name__ == "__main__":
    unittest.main()
