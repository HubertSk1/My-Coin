import cryptography.hazmat.primitives.serialization as serial
import cryptography.exceptions as crypto_exceptions

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

from pprint import pprint
import json
import random
from typing import Any

import requests

def verify(public_key: str, sign: str, data: dict[str,Any]):
    pub_key = serial.load_pem_public_key(public_key.encode())
    if isinstance(pub_key, ec.EllipticCurvePublicKey):
        print("It' public key")
        signature = bytes.fromhex(sign)
        print(f"signature = {sign}")
        separators = (",", ":")
        serial_contents = json.dumps(
                obj=data, sort_keys=True, separators=separators
            ).encode()
        print(f"serial_contents = {serial_contents}")
        pub_key.verify(signature, serial_contents, ec.ECDSA(hashes.SHA256()))
    else:
        print("Unsupported public key format")
        return False

def sign(
    contents: dict[str,Any],
    private_key: ec.EllipticCurvePrivateKey,
    ):
    separators = (",", ":")
    print(contents)
    serialized_contents = json.dumps(
        contents, sort_keys=True, separators=separators
    ).encode()

    signed = private_key.sign(
        serialized_contents, ec.ECDSA(hashes.SHA256())
    ).hex()  # DER encoded
    print(f"serial_contents = {serialized_contents}")
    print(f"signature = {signed}")
    return signed
