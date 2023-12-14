from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from pprint import pprint
import json
import random
from typing import Any


def verify(message: str, signature : bytes, public_key:str):
        key = RSA.import_key(public_key)
        h = SHA256.new(message.encode('utf-8'))
        try:
            pkcs1_15.new(key).verify(h, signature)
            return True  
        except Exception:
            return False
        


def sign(message: bytes | str, private_key:str)->bytes:
        key = RSA.import_key(private_key)
        match message:
            case bytes():
                h = SHA256.new(message)
            case str():
                h = SHA256.new(message.encode('utf-8'))
            case _:
                raise TypeError('Unsupported type')
        signature = pkcs1_15.new(key).sign(h)
        return signature