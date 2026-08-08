"""
Unit tests for apps.shared_core.security module.
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from jose import jwt
from apps.shared_core import security
from apps.shared_core.config import Settings


class TestSecurityFunctions:
    """Test suite for security helper functions."""

    def test_verify_password_bcrypt_success(self, monkeypatch):
        """Test password verification with a correct password using bcrypt."""
        # Mock bcrypt to simulate successful check
        def mock_checkpw(plain, hashed):
            return True

        monkeypatch.setattr("apps.shared_core.security._bcrypt.checkpw", mock_checkpw)

        plain_password = "my_secure_password"
        hashed_password = "$2b$12$..."
        
        assert security.verify_password(plain_password, hashed_password) is True

    def test_verify_password_bcrypt_failure(self, monkeypatch):
        """Test password verification with an incorrect password using bcrypt."""
        # Mock bcrypt to simulate failure
        def mock_checkpw(plain, hashed):
            return False

        monkeypatch.setattr("apps.shared_core.security._bcrypt.checkpw", mock_checkpw)

        plain_password = "wrong_password"
        hashed_password = "$2b$12$..."
        
        assert security.verify_password(plain_password, hashed_password) is False

    def test_get_password_hash_bcrypt(self, monkeypatch):
        """Test password hashing using bcrypt."""
        # Mock bcrypt to return a predictable hash
        expected_hash = "$2b$12$mocked_hash_value"
        def mock_gen_salt(rounds):
            return b"$2b$12$salt$"
        def mock_hashpw(password, salt):
            return expected_hash.encode()

        monkeypatch.setattr("apps.shared_core.security._bcrypt.gensalt", mock_gen_salt)
        monkeypatch.setattr("apps.shared_core.security._bcrypt.hashpw", mock_hashpw)

        password = "new_password"
        result_hash = security.get_password_hash(password)
        
        assert result_hash == expected_hash

    @patch('apps.shared_core.jwt_keys.signing_key')
    @patch('apps.shared_core.jwt_keys.algorithms')
    def test_create_access_token(self, mock_algorithms, mock_signing_key):
        """Test creation of an access token."""
        mock_signing_key.return_value = "test_secret"
        mock_algorithms.return_value = ["HS256"]
        subject = "123"
        extra_payload = {"role": "admin"}

        token = security.create_access_token(subject, extra_payload)

        # Decode the token to check its contents
        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["sub"] == subject
        assert payload["type"] == "access"
        assert payload["role"] == "admin"
        assert "exp" in payload
        # Check if expiry is roughly in the future (within 31 minutes, given default 30 min expiry)
        now = datetime.now(timezone.utc)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert now < exp_time <= now + datetime.timedelta(minutes=31)

    @patch('apps.shared_core.jwt_keys.signing_key')
    @patch('apps.shared_core.jwt_keys.algorithms')
    def test_create_refresh_token(self, mock_algorithms, mock_signing_key):
        """Test creation of a refresh token."""
        mock_signing_key.return_value = "test_secret"
        mock_algorithms.return_value = ["HS256"]
        subject = "123"

        token = security.create_refresh_token(subject)

        payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
        assert payload["sub"] == subject
        assert payload["type"] == "refresh"
        assert "jti" in payload # Check if JTI is included
        assert "exp" in payload
        # Check if expiry is roughly in the future (within 15 days, given default 14 day expiry)
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert now < exp_time <= now + timedelta(days=15)

    @patch('apps.shared_core.jwt_keys.verify_key')
    @patch('apps.shared_core.jwt_keys.algorithms')
    def test_decode_token(self, mock_algorithms, mock_verify_key):
        """Test decoding a valid token."""
        mock_verify_key.return_value = "test_secret"
        mock_algorithms.return_value = ["HS256"]
        subject = "456"
        token = jwt.encode({"sub": subject, "type": "access"}, "test_secret", algorithm="HS256")

        payload = security.decode_token(token)

        assert payload["sub"] == subject
        assert payload["type"] == "access"

    def test_cookie_kwargs(self):
        """Test generation of cookie attributes."""
        settings = Settings(ENVIRONMENT="production", COOKIE_SECURE=True, COOKIE_SAMESITE="strict")
        max_age = 1800
        
        kwargs = security.cookie_kwargs(max_age)

        expected = {
            "httponly": True,
            "secure": True, # Because COOKIE_SECURE is True or environment is production
            "samesite": "strict",
            "max_age": 1800,
            "path": "/",
        }
        assert kwargs == expected