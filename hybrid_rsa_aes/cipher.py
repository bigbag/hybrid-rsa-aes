import base64
import json
import os
import uuid
from typing import Dict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class HybridCipher:
    def _get_nonce_length(self):
        return algorithms.AES.block_size // 8

    def _build_sync_key(self, key: bytes):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(key)
        return digest.finalize()

    def _encrypt_sync(self, data, key: bytes):
        payload = json.dumps({"v": data})

        key = self._build_sync_key(key)
        nonce = os.urandom(self._get_nonce_length())

        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(payload.encode("utf-8")) + encryptor.finalize()
        return base64.b64encode(nonce + encrypted).decode()

    def _decrypt_sync(self, cipher_text: str, key: bytes):
        key = self._build_sync_key(key)
        nonce_length = self._get_nonce_length()

        raw = base64.b64decode(cipher_text)
        nonce, message = raw[:nonce_length], raw[nonce_length:]
        decryptor = Cipher(
            algorithms.AES(key), modes.CTR(nonce), backend=default_backend()
        ).decryptor()
        payload = decryptor.update(message) + decryptor.finalize()

        return json.loads(payload)["v"]

    def encrypt(self, rsa_public_key, data: Dict):
        password = uuid.uuid4().hex
        encrypted_payload = self._encrypt_sync(data, password.encode())

        encrypted_password = base64.b64encode(
            rsa_public_key.encrypt(
                password.encode("utf-8"),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        ).decode()

        return f"{encrypted_password};{encrypted_payload}"

    def decrypt(self, rsa_private_key, cipher_text: str):
        encrypted_password, encrypted_payload = cipher_text.split(";")

        password = rsa_private_key.decrypt(
            base64.b64decode(encrypted_password),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return self._decrypt_sync(encrypted_payload, password)
