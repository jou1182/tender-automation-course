# Al-Rawaf V4 Security Vault - Fernet Edition
# Upgraded from XOR+Base64 (obfuscation) to AES-128-CBC via Fernet (real cryptography).
# Backward-compatible: still reads old VAULT: (XOR) format during migration period.
import base64
import os
from pathlib import Path

KEY_FILE = Path(__file__).parent / "vault.key"

if not KEY_FILE.exists():
    raise FileNotFoundError(
        f"CRITICAL: vault.key missing at {KEY_FILE}! "
        "System cannot decrypt secrets. Restore from secure backup."
    )

with open(KEY_FILE, "rb") as f:
    _KEY_BYTES = f.read()

# Detect key type: Fernet keys are 44-byte URL-safe base64 strings
def _is_fernet_key(key: bytes) -> bool:
    try:
        from cryptography.fernet import Fernet
        Fernet(key)
        return True
    except Exception:
        return False

_USE_FERNET = _is_fernet_key(_KEY_BYTES)

if _USE_FERNET:
    from cryptography.fernet import Fernet
    _fernet = Fernet(_KEY_BYTES)


def encrypt_val(plaintext: str) -> str:
    """Encrypts a credential for storage in .env file."""
    if not plaintext:
        return ""
    if _USE_FERNET:
        return "FERNET:" + _fernet.encrypt(plaintext.encode()).decode()
    else:
        # Legacy XOR fallback (only for old vault.key files)
        result = bytearray()
        for i in range(len(plaintext)):
            result.append(ord(plaintext[i]) ^ _KEY_BYTES[i % len(_KEY_BYTES)])
        return "VAULT:" + base64.b64encode(result).decode()


def decrypt_val(vault_text: str) -> str:
    """Decrypts a credential. Handles both FERNET: and legacy VAULT: (XOR) formats."""
    if not vault_text:
        return vault_text

    # New Fernet format
    if vault_text.startswith("FERNET:"):
        try:
            return _fernet.decrypt(vault_text[7:].encode()).decode()
        except Exception as e:
            raise ValueError(f"CRITICAL: Failed to decrypt FERNET value. vault.key may be wrong. Error: {e}")

    # Legacy XOR format (backward compatibility during migration)
    if vault_text.startswith("VAULT:"):
        try:
            raw = base64.b64decode(vault_text[6:])
            result = bytearray()
            for i in range(len(raw)):
                result.append(raw[i] ^ _KEY_BYTES[i % len(_KEY_BYTES)])
            return result.decode()
        except Exception:
            return vault_text

    # Plain text (not encrypted)
    return vault_text
