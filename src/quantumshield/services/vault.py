"""Local authenticated-encryption vault with wrapped per-object keys."""

import base64
import json
import os
import secrets
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class VaultError(Exception):
    """Base class for vault errors."""


class VaultConfigurationError(VaultError):
    """Raised when no valid master key is configured."""


class VaultService:
    """Encrypts file content using a random DEK wrapped by a configured KEK.

    Master key must be 32 random bytes encoded as URL-safe base64. In production,
    replace local KEK handling with a KMS/HSM and use tenant-scoped authorization.
    """

    def __init__(self, root: Path, master_key: str, max_bytes: int = 10 * 1024 * 1024):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        if not master_key:
            raise VaultConfigurationError(
                "QUANTUMSHIELD_MASTER_KEY is required for vault operations"
            )
        try:
            key = base64.urlsafe_b64decode(master_key.encode())
        except Exception as exc:
            raise VaultConfigurationError("master key must be URL-safe base64") from exc
        if len(key) != 32:
            raise VaultConfigurationError("master key must decode to exactly 32 bytes")
        self._kek = key

    def encrypt(self, filename: str, content: bytes) -> dict[str, Any]:
        if len(content) > self.max_bytes:
            raise VaultError(f"file exceeds configured {self.max_bytes}-byte limit")
        safe_name = Path(filename).name[:180] or "file.bin"
        object_id = secrets.token_hex(16)
        dek = AESGCM.generate_key(bit_length=256)
        data_nonce = os.urandom(12)
        wrap_nonce = os.urandom(12)
        ciphertext = AESGCM(dek).encrypt(data_nonce, content, object_id.encode())
        wrapped_dek = AESGCM(self._kek).encrypt(wrap_nonce, dek, object_id.encode())
        envelope = {
            "version": 1,
            "object_id": object_id,
            "filename": safe_name,
            "data_nonce": base64.b64encode(data_nonce).decode(),
            "wrap_nonce": base64.b64encode(wrap_nonce).decode(),
            "wrapped_dek": base64.b64encode(wrapped_dek).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        }
        target = self.root / f"{object_id}.json"
        target.write_text(json.dumps(envelope), encoding="utf-8")
        return {"object_id": object_id, "filename": safe_name, "bytes": len(content), "algorithm": "AES-256-GCM"}

    def decrypt(self, object_id: str) -> tuple[str, bytes]:
        if not object_id.isalnum() or len(object_id) != 32:
            raise VaultError("invalid object identifier")
        target = self.root / f"{object_id}.json"
        if not target.exists():
            raise VaultError("vault object not found")
        envelope = json.loads(target.read_text(encoding="utf-8"))
        if envelope.get("object_id") != object_id or envelope.get("version") != 1:
            raise VaultError("invalid vault envelope")
        aad = object_id.encode()
        dek = AESGCM(self._kek).decrypt(
            base64.b64decode(envelope["wrap_nonce"]),
            base64.b64decode(envelope["wrapped_dek"]),
            aad,
        )
        plaintext = AESGCM(dek).decrypt(
            base64.b64decode(envelope["data_nonce"]),
            base64.b64decode(envelope["ciphertext"]),
            aad,
        )
        return envelope["filename"], plaintext
