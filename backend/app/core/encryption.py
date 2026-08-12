import base64
import hashlib
from cryptography.fernet import Fernet
from app.core.config import settings


def _get_fernet_key() -> bytes:
    """Derive a 32-byte URL-safe base64 Fernet key from settings.SECRET_KEY."""
    digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_token(token: str) -> str:
    """Encrypt a plain text OAuth token string."""
    if not token:
        return ""
    try:
        fernet = Fernet(_get_fernet_key())
        return fernet.encrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        # Fallback to plain if cipher initialization fails (e.g. mock tests)
        return token


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted OAuth token string back to plain text."""
    if not encrypted_token:
        return ""
    try:
        fernet = Fernet(_get_fernet_key())
        return fernet.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
    except Exception:
        # Fallback if unencrypted / legacy token
        return encrypted_token
