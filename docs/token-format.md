# Version 1 token format

`HybridCipher.encrypt` returns a UTF-8 JSON object with exactly these fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `v` | integer | Format version; v1 requires `1`. |
| `ek` | Base64URL string | RSA-OAEP-SHA-256 encrypted 32-byte AES key. |
| `n` | Base64URL string | A 12-byte AES-256-GCM nonce. |
| `ct` | Base64URL string | AES-256-GCM ciphertext followed by its 16-byte authentication tag. |

Base64URL uses the URL-safe alphabet without padding. Tokens reject unknown or missing fields, non-string encoded fields, invalid Base64URL, non-12-byte nonces, ciphertext shorter than the authentication tag, and versions other than `1`.

The library uses the fixed associated-data byte string `hybrid-rsa-aes:v1`. This binds the ciphertext to the version. The token is an interchange format, not a key-management protocol: applications must protect private keys, choose recipients, and implement replay handling when needed.
