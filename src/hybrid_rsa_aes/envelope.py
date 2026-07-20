from __future__ import annotations

import base64
import binascii
import json
import re
from dataclasses import dataclass
from typing import Final

from .errors import InvalidTokenError

_VERSION: Final = 1
_FIELDS: Final = frozenset({"v", "ek", "n", "ct"})
_NONCE_BYTES: Final = 12
_TAG_BYTES: Final = 16
_BASE64URL: Final = re.compile(r"[A-Za-z0-9_-]*\Z")


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: object, field: str) -> bytes:
    if not isinstance(value, str) or not value or not _BASE64URL.fullmatch(value):
        raise InvalidTokenError(f"token field {field!r} is not valid Base64URL")
    if len(value) % 4 == 1:
        raise InvalidTokenError(f"token field {field!r} has invalid Base64URL length")
    try:
        return base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
    except (ValueError, binascii.Error) as error:
        raise InvalidTokenError(f"token field {field!r} is not valid Base64URL") from error


@dataclass(frozen=True, slots=True)
class Envelope:
    encrypted_key: bytes
    nonce: bytes
    ciphertext: bytes

    def to_token(self) -> str:
        return json.dumps(
            {
                "v": _VERSION,
                "ek": _encode(self.encrypted_key),
                "n": _encode(self.nonce),
                "ct": _encode(self.ciphertext),
            },
            separators=(",", ":"),
            sort_keys=True,
        )


def parse_envelope(token: object) -> Envelope:
    if not isinstance(token, str):
        raise InvalidTokenError("token must be a string")
    try:
        value = json.loads(token)
    except json.JSONDecodeError as error:
        raise InvalidTokenError("token is not valid JSON") from error
    if not isinstance(value, dict) or set(value) != _FIELDS:
        raise InvalidTokenError("token must contain exactly v, ek, n, and ct")
    if type(value["v"]) is not int or value["v"] != _VERSION:
        raise InvalidTokenError("token has an unsupported version")

    nonce = _decode(value["n"], "n")
    ciphertext = _decode(value["ct"], "ct")
    if len(nonce) != _NONCE_BYTES:
        raise InvalidTokenError("token nonce must be 12 bytes")
    if len(ciphertext) < _TAG_BYTES:
        raise InvalidTokenError("token ciphertext is shorter than its authentication tag")
    return Envelope(encrypted_key=_decode(value["ek"], "ek"), nonce=nonce, ciphertext=ciphertext)
