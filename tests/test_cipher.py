import json

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from hybrid_rsa_aes import HybridCipher, InvalidKeyError, PayloadSerializationError


def test_encrypt_decrypt_round_trip_for_json_values(private_key: RSAPrivateKey) -> None:
    cipher = HybridCipher()
    payloads = [{"name": "Ada", "items": [1, True, None]}, ["a", 2], "text", 7, False, None]

    for payload in payloads:
        token = cipher.encrypt(private_key.public_key(), payload)
        assert cipher.decrypt(private_key, token) == payload


def test_each_encryption_uses_fresh_material(private_key: RSAPrivateKey) -> None:
    cipher = HybridCipher()

    first = cipher.encrypt(private_key.public_key(), {"same": "payload"})
    second = cipher.encrypt(private_key.public_key(), {"same": "payload"})

    assert first != second
    assert json.loads(first)["v"] == 1


def test_rejects_non_json_payload(private_key: RSAPrivateKey) -> None:
    with pytest.raises(PayloadSerializationError):
        HybridCipher().encrypt(private_key.public_key(), {"not_json": {1, 2}})


def test_rejects_non_rsa_and_short_keys(private_key: RSAPrivateKey) -> None:
    cipher = HybridCipher()
    short_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)

    with pytest.raises(InvalidKeyError):
        cipher.encrypt(object(), {"value": 1})
    with pytest.raises(InvalidKeyError):
        cipher.encrypt(short_key.public_key(), {"value": 1})
    with pytest.raises(InvalidKeyError):
        cipher.decrypt(object(), "{}")
