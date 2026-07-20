from cryptography.hazmat.primitives.asymmetric import rsa

from hybrid_rsa_aes import HybridCipher

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
payload = {"message": "authenticated hybrid encryption", "version": 1}

cipher = HybridCipher()
token = cipher.encrypt(public_key, payload)
decrypted = cipher.decrypt(private_key, token)

assert decrypted == payload
