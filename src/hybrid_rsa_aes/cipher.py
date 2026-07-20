from __future__ import annotations

import json
import os
from typing import Final, NoReturn, TypeAlias, cast

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .envelope import Envelope, parse_envelope
from .errors import DecryptionError, InvalidKeyError, PayloadSerializationError

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
_KEY_BYTES: Final = 32
_NONCE_BYTES: Final = 12
_ASSOCIATED_DATA: Final = b"hybrid-rsa-aes:v1"
_MIN_RSA_BITS: Final = 2048
_OAEP: Final = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None,
)


def _validate_public_key(key: object) -> RSAPublicKey:
    if not isinstance(key, RSAPublicKey) or key.key_size < _MIN_RSA_BITS:
        raise InvalidKeyError("encryption requires an RSA public key of at least 2048 bits")
    return key


def _validate_private_key(key: object) -> RSAPrivateKey:
    if not isinstance(key, RSAPrivateKey) or key.key_size < _MIN_RSA_BITS:
        raise InvalidKeyError("decryption requires an RSA private key of at least 2048 bits")
    return key


def _reject_nonstandard_json_constant(value: str) -> NoReturn:
    raise ValueError(f"non-standard JSON constant {value!r}")


class HybridCipher:
    """Encrypt and decrypt JSON values using RSA-OAEP-wrapped AES-256-GCM keys."""

    def encrypt(self, rsa_public_key: RSAPublicKey, data: JSONValue) -> str:
        public_key = _validate_public_key(rsa_public_key)
        try:
            plaintext = json.dumps(
                data,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        except (TypeError, ValueError) as error:
            raise PayloadSerializationError("data must be JSON serializable") from error

        data_encryption_key = AESGCM.generate_key(bit_length=_KEY_BYTES * 8)
        nonce = os.urandom(_NONCE_BYTES)
        ciphertext = AESGCM(data_encryption_key).encrypt(nonce, plaintext, _ASSOCIATED_DATA)
        try:
            encrypted_key = public_key.encrypt(data_encryption_key, _OAEP)
        except ValueError as error:
            raise InvalidKeyError("RSA public key cannot wrap an AES-256 key") from error
        return Envelope(encrypted_key=encrypted_key, nonce=nonce, ciphertext=ciphertext).to_token()

    def decrypt(self, rsa_private_key: RSAPrivateKey, cipher_text: str) -> JSONValue:
        private_key = _validate_private_key(rsa_private_key)
        envelope = parse_envelope(cipher_text)
        try:
            data_encryption_key = private_key.decrypt(envelope.encrypted_key, _OAEP)
            if len(data_encryption_key) != _KEY_BYTES:
                raise ValueError("unwrapped key has an invalid length")
            plaintext = AESGCM(data_encryption_key).decrypt(
                envelope.nonce,
                envelope.ciphertext,
                _ASSOCIATED_DATA,
            )
            return cast(
                JSONValue,
                json.loads(
                    plaintext.decode("utf-8"),
                    parse_constant=_reject_nonstandard_json_constant,
                ),
            )
        except (InvalidTag, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            raise DecryptionError("token could not be authenticated and decrypted") from error
