import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
import hashlib

from Crypto.Cipher import PKCS1_OAEP

user_input = "gwiazda"

seed = hashlib.sha256(user_input.encode('utf-8')).digest()
random_generator = Random.new().read
key = RSA.generate(1024, random_generator) #generate pub and priv key

publickey = key.publickey() # pub key export for exchange
publickey.public_key()

message="zakodowane".encode()
cipher = PKCS1_OAEP.new(publickey)
encrypted = cipher.encrypt(message)

print('encrypted message:', encrypted) 
cipher = PKCS1_OAEP.new(key)
decrypted = cipher.decrypt(encrypted)
print('decrypted:', decrypted.decode('utf-8'))