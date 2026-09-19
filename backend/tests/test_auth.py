import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import app.auth as auth


FAKE_SETTINGS = SimpleNamespace(
    admin_username="admin",
    admin_password="super-secret-test-password",
    session_ttl_minutes=60,
)


class AuthTokenTests(unittest.TestCase):
    def test_issue_and_verify_roundtrip(self):
        with patch.object(auth, "get_settings", return_value=FAKE_SETTINGS):
            token = auth.issue_token("admin")
            self.assertEqual(auth.verify_token(token), "admin")

    def test_tampered_token_is_rejected(self):
        with patch.object(auth, "get_settings", return_value=FAKE_SETTINGS):
            token = auth.issue_token("admin")
            payload, sig = token.split(".")
            tampered = f"{payload}.{'A' if sig[0] != 'A' else 'B'}{sig[1:]}"
            self.assertIsNone(auth.verify_token(tampered))

    def test_expired_token_is_rejected(self):
        # Issue a token whose exp lies clearly in the past, regardless of clock drift.
        with patch.object(auth, "get_settings", return_value=FAKE_SETTINGS):
            with patch.object(auth.time, "time", return_value=time.time() - 7200):
                token = auth.issue_token("admin")
            self.assertIsNone(auth.verify_token(token))

    def test_login_fails_closed_without_password(self):
        no_password = SimpleNamespace(
            admin_username="admin", admin_password="", session_ttl_minutes=60
        )
        with patch.object(auth, "get_settings", return_value=no_password):
            token = auth.issue_token("admin")
            self.assertIsNone(auth.verify_token(token))

    def test_wrong_user_is_rejected(self):
        with patch.object(auth, "get_settings", return_value=FAKE_SETTINGS):
            token = auth.issue_token("someone-else")
            self.assertIsNone(auth.verify_token(token))


if __name__ == "__main__":
    unittest.main()
