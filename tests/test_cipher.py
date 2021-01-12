from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

from hybrid_rsa_aes import HybridCipher


def test_encrypt_decrypt():
    rsa_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    rsa_public_key = rsa_private_key.public_key()

    encrypt_message = HybridCipher().encrypt(rsa_public_key=rsa_public_key, data={"test": "demo"})

    decrypt_message = HybridCipher().decrypt(
        rsa_private_key=rsa_private_key, cipher_text=encrypt_message
    )
    assert "test" in decrypt_message and decrypt_message["test"] == "demo"
