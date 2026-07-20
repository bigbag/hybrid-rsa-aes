import json

import pytest

from hybrid_rsa_aes.envelope import Envelope, parse_envelope
from hybrid_rsa_aes.errors import InvalidTokenError

_VALID_TOKEN = {
    "v": 1,
    "ek": "a2V5",
    "n": "bm5ubm5ubm5ubm5u",
    "ct": "Y2lwaGVydGV4dGNpcGhlcnRleHQ",
}


def test_envelope_serializes_the_v1_schema() -> None:
    token = Envelope(encrypted_key=b"key", nonce=b"n" * 12, ciphertext=b"ciphertext" * 2).to_token()

    assert json.loads(token) == {
        "ct": _VALID_TOKEN["ct"],
        "ek": "a2V5",
        "n": _VALID_TOKEN["n"],
        "v": 1,
    }


def test_envelope_round_trips_binary_fields() -> None:
    envelope = Envelope(encrypted_key=b"key", nonce=b"n" * 12, ciphertext=b"ciphertext" * 2)

    assert parse_envelope(envelope.to_token()) == envelope


@pytest.mark.parametrize(
    "token",
    [
        "not json",
        "[]",
        json.dumps({"v": 1, "ek": "a2V5", "n": _VALID_TOKEN["n"]}),
        json.dumps({**_VALID_TOKEN, "v": 2}),
        json.dumps({**_VALID_TOKEN, "n": "bm5ubg"}),
        json.dumps({**_VALID_TOKEN, "ct": "@@@"}),
        json.dumps({**_VALID_TOKEN, "extra": True}),
    ],
)
def test_parse_rejects_invalid_v1_tokens(token: str) -> None:
    with pytest.raises(InvalidTokenError):
        parse_envelope(token)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ek", "a"),
        ("ek", None),
        ("n", 12),
        ("ct", False),
        ("v", True),
    ],
)
def test_parse_rejects_malformed_or_wrongly_typed_fields(field: str, value: object) -> None:
    token = {**_VALID_TOKEN, field: value}

    with pytest.raises(InvalidTokenError):
        parse_envelope(json.dumps(token))
