import cryptography.hazmat.primitives.serialization as serial
import cryptography.exceptions as crypto_exceptions

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

from pprint import pprint
import json
import random
from typing import Any

import requests

def verify(public_key: str, signature: str, data: bytes):
    pub_key = serial.load_pem_public_key(public_key.encode())
    if isinstance(pub_key, ec.EllipticCurvePublicKey):
        print("It' public key")
        print(f"signature = {signature}")
        _signature = bytes.fromhex(signature)
        print(f"serial_contents = {data}")
        pub_key.verify(_signature, data, ec.ECDSA(hashes.SHA256()))
    else:
        raise Exception("Unsupported public key format")

def sign(
    data: bytes,
    private_key: ec.EllipticCurvePrivateKey,
    ):
    print(f"serial_contents = {data}")
    signed = private_key.sign(
        data, ec.ECDSA(hashes.SHA256())
    ).hex()  # DER encoded
    print(f"signature = {signed}")
    return signed
