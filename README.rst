hybrid-rsa-aes
=======================================================================

.. image:: https://github.com/bigbag/hybrid-rsa-aes/workflows/CI/badge.svg
   :target: https://github.com/bigbag/hybrid-rsa-aes/actions?query=workflow%3ACI
.. image:: https://img.shields.io/pypi/v/hybrid-rsa-aes.svg
   :target: https://pypi.python.org/pypi/hybrid-rsa-aes


**hybrid-rsa-aes** is a helper for hybrid AES-RSA encryption.


Installation
------------
hybrid-rsa-aes is available on PyPI.
Use pip to install:

    $ pip install hybrid-rsa-aes

Basic Usage
-----------

.. code:: python

    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa

    from hybrid_rsa_aes import HybridCipher

    rsa_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    rsa_public_key = rsa_private_key.public_key()

    encrypt_message = HybridCipher().encrypt(rsa_public_key=rsa_public_key, data={"test": "demo"})
    
    decrypt_message = HybridCipher().decrypt(
        rsa_private_key=rsa_private_key, cipher_text=encrypt_message
    )
    assert "test" in decrypt_message and decrypt_message["test"] == "demo"

License
-------

hybrid-rsa-aes is developed and distributed under the Apache 2.0 license.