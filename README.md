# hybrid-rsa-aes

Authenticated hybrid RSA and AES encryption for JSON payloads.

## Requirements

- Python 3.11–3.14
- An RSA key pair of at least 2048 bits

## Install

```console
uv add hybrid-rsa-aes
```

```console
pip install hybrid-rsa-aes
```

## Quick start

```python
from cryptography.hazmat.primitives.asymmetric import rsa

from hybrid_rsa_aes import HybridCipher

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

cipher = HybridCipher()
token = cipher.encrypt(public_key, {"account_id": 42, "roles": ["reader"]})
payload = cipher.decrypt(private_key, token)
assert payload == {"account_id": 42, "roles": ["reader"]}
```

`encrypt` accepts standard JSON values and returns a text token. `decrypt` returns the original JSON value. Tokens are JSON objects with version `v`, wrapped-key `ek`, nonce `n`, and ciphertext `ct` fields.

## Security properties

Each message uses a fresh random AES-256 key and a fresh 96-bit nonce. AES-256-GCM encrypts and authenticates the UTF-8 JSON payload, and RSA-OAEP with SHA-256 encrypts the AES key. The v1 marker is AES-GCM associated data, so a token cannot be relabelled as another format version.

AES-GCM detects modification: treat `DecryptionError` as an invalid, modified, or wrong-key token. Treat `InvalidTokenError` as malformed or unsupported token syntax. `InvalidKeyError` means the supplied key is not an RSA key of at least 2048 bits. `PayloadSerializationError` means an encryption payload was not standard JSON.

This library protects payload confidentiality and integrity. It does not manage private-key storage, key rotation, replay protection, recipient identity, or application authorization.

## Migrating from 0.x

1.0.0 is a breaking security rewrite. It replaces AES-CTR with AES-256-GCM, uses a random AES key instead of a UUID-derived key, and emits versioned JSON tokens. **0.x ciphertexts are not supported** and must be decrypted by a 0.x deployment before migration if their plaintext must be retained. The `HybridCipher().encrypt(public_key, data)` and `decrypt(private_key, token)` calling pattern remains, but payloads may now be any JSON value and callers must handle the documented exceptions.

## Example

```console
uv run python examples/basic_usage.py
```

## Development

```console
uv sync
make lint
make test
make build
```

## License

hybrid-rsa-aes is distributed under the Apache License 2.0.
