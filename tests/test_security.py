import json
import os

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from hybrid_rsa_aes import DecryptionError, HybridCipher, InvalidTokenError
from hybrid_rsa_aes.envelope import Envelope


def _oaep_wrap(public_key: RSAPublicKey, key: bytes) -> bytes:
    return public_key.encrypt(
        key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def _authenticated_token(private_key: RSAPrivateKey, plaintext: bytes) -> str:
    data_encryption_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    ciphertext = AESGCM(data_encryption_key).encrypt(nonce, plaintext, b"hybrid-rsa-aes:v1")
    return Envelope(
        encrypted_key=_oaep_wrap(private_key.public_key(), data_encryption_key),
        nonce=nonce,
        ciphertext=ciphertext,
    ).to_token()


def test_tampered_ciphertext_is_rejected(private_key: RSAPrivateKey) -> None:
    cipher = HybridCipher()
    envelope = json.loads(cipher.encrypt(private_key.public_key(), {"role": "user"}))
    envelope["ct"] = ("A" if envelope["ct"][0] != "A" else "B") + envelope["ct"][1:]

    with pytest.raises(DecryptionError):
        cipher.decrypt(private_key, json.dumps(envelope, separators=(",", ":")))


def test_wrong_private_key_is_rejected(private_key: RSAPrivateKey) -> None:
    token = HybridCipher().encrypt(private_key.public_key(), {"message": "secret"})
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with pytest.raises(DecryptionError):
        HybridCipher().decrypt(wrong_key, token)


def test_authenticated_nonstandard_json_constant_is_normalized_to_decryption_error(
    private_key: RSAPrivateKey,
) -> None:
    token = _authenticated_token(private_key, b"NaN")

    with pytest.raises(DecryptionError):
        HybridCipher().decrypt(private_key, token)


def test_wrapped_key_with_wrong_length_is_normalized_to_decryption_error(
    private_key: RSAPrivateKey,
) -> None:
    token = Envelope(
        encrypted_key=_oaep_wrap(private_key.public_key(), b"short"),
        nonce=b"n" * 12,
        ciphertext=b"c" * 16,
    ).to_token()

    with pytest.raises(DecryptionError):
        HybridCipher().decrypt(private_key, token)


def test_legacy_semicolon_token_is_not_accepted(private_key: RSAPrivateKey) -> None:
    with pytest.raises(InvalidTokenError):
        HybridCipher().decrypt(private_key, "old-key;old-payload")
