from dataclasses import dataclass

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jwcrypto.jwk import JWK


@dataclass
class JWKey:
    iss: str
    alg: str
    key: JWK

    @classmethod
    def from_json(cls, iss: str, alg: str, json_key: str) -> "JWKey":
        return cls(iss=iss, alg=alg, key=JWK.from_json(json_key))

    @classmethod
    def from_pem(cls, iss: str, alg: str, pem_key: bytes) -> "JWKey":
        return cls(iss=iss, alg=alg, key=JWK.from_pem(pem_key))

    def get_rsa_public_key(self):
        return serialization.load_pem_public_key(
            self.key.export_to_pem(),
            backend=default_backend(),
        )

    def get_rsa_private_key(self):
        return serialization.load_pem_private_key(
            self.key.export_to_pem(private_key=True, password=None),
            password=None,
            backend=default_backend(),
        )
