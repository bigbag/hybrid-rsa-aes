class HybridCipherError(Exception):
    """Base class for errors raised by hybrid-rsa-aes."""


class InvalidKeyError(HybridCipherError):
    """Raised when a supplied RSA key has an unsupported type or size."""


class PayloadSerializationError(HybridCipherError):
    """Raised when a payload cannot be encoded as standard JSON."""


class InvalidTokenError(HybridCipherError):
    """Raised when a token is not a structurally valid v1 envelope."""


class DecryptionError(HybridCipherError):
    """Raised when a structurally valid token cannot be authenticated or decoded."""
