import asyncio
import websockets
import aioconsole
import random 
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Message import Message_Generator
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes

class Node:
    def __init__(self,pass_phrase,port,ip):
        self.ip = ip
        self.port = port
        self.pass_phrase = pass_phrase
        self._private_key,self.public_key = self.generate_keys(pass_phrase)
        self.list_of_nodes = {}#format {"public_key":'ip:port',}
        self.mg = Message_Generator(f"{self.ip}:{self.port}",self.public_key)
        self.Home_Node_Public = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCRmK3JDQObgn+RKUSbo5zzvazu
NZ7QP/fx7T4kWLRxWh45D8D3Tojm45Jr4qTo4WigJ4+3blznlxg+kaa31YXQJPQw
o+XXkoDGDpZQ+mA7IxBlvoxkG6PAZ9yJU9b1tMsaXGzKcGDNbGyc7CoSyyqouTWe
9NWr+64beIA1ER7NhQIDAQAB
-----END PUBLIC KEY-----"""
        self.Home_Node_name = "127.0.0.1:9001"

    def generate_keys(self,input_word: str) -> (str, str):
        """Derive a private and public key pair from the user input using a deterministic method."""
        
        # Seed python's random with the hash of the input_word for a bit more entropy.
        seed = int(hashlib.sha256(input_word.encode('utf-8')).hexdigest(), 16)
        random.seed(seed)
        
        # A function to produce deterministic random bytes using Python's random
        def deterministic_random_bytes(n):
            return bytes([random.randint(0, 255) for _ in range(n)])
        
        # Use a constant value for reproducible key generation
        random_generator = deterministic_random_bytes
        
        key = RSA.generate(1024, randfunc=random_generator) 
        private_key = key.export_key().decode('utf-8')
        public_key = key.publickey().export_key().decode('utf-8')
        return (private_key, public_key)
    
    def hybrid_encrypt(self,message, public_key):
        rsa_public_key = RSA.import_key(public_key)
        # Generate random symmetric AES key
        aes_key = get_random_bytes(16)
        
        # Encrypt message using AES
        cipher_aes = AES.new(aes_key, AES.MODE_EAX)
        nonce = cipher_aes.nonce
        ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode('utf-8'))
        
        # Encrypt the AES key using RSA
        cipher_rsa = PKCS1_OAEP.new(rsa_public_key)
        encrypted_aes_key = cipher_rsa.encrypt(aes_key)
        
        return (encrypted_aes_key, nonce, ciphertext)

    def hybrid_decrypt(self,encrypted_data, private_key):

        rsa_private_key = RSA.import_key(private_key)
        encrypted_aes_key, nonce, ciphertext = encrypted_data
        
        # Decrypt the AES key using RSA
        cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
        decrypted_aes_key = cipher_rsa.decrypt(encrypted_aes_key)
        
        # Decrypt the message using AES
        cipher_aes = AES.new(decrypted_aes_key, AES.MODE_EAX, nonce=nonce)
        decrypted_message = cipher_aes.decrypt(ciphertext)
        
        return decrypted_message.decode('utf-8')
    
    async def send_message(self,name,message): #name format ip:port
        uri = f"ws://{name}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)
            await websocket.close()

    def sign_message(self, message, private_key):
        key = RSA.import_key(private_key)
        if type(message) ==bytes:
            h = SHA256.new(message)
        else:    
            h = SHA256.new(message.encode('utf-8'))
        signature = pkcs1_15.new(key).sign(h)
        return signature

    async def analyze_message(message):
        pass # The implementation will differ for Home Node and User Node

    def verify_signature(self,message, signature, public_key):
        key = RSA.import_key(public_key)
        h = SHA256.new(message.encode('utf-8'))
        try:
            pkcs1_15.new(key).verify(h, signature)
            return True  
        except Exception:
            return False  

    async def websocket_listener(self, websocket, path):
        async for message in websocket:
            await self.analyze_message(message)
                

    async def start_server(self):
        server = await websockets.serve(self.websocket_listener, self.ip, self.port)
        await asyncio.gather(self.node_live(), server.wait_closed())

    async def node_live(self):
        while True:
            user_input = await aioconsole.ainput("Enter_Home_Node_Commends")
            if user_input == 'quit':
                break
            print(f"You entered: {user_input}")