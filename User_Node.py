import asyncio
import websockets
import aioconsole
import json
import base64
import Crypto.Random 
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Message import Message_Generator
import random 
import hashlib
Home_Node_Public = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCRmK3JDQObgn+RKUSbo5zzvazu
NZ7QP/fx7T4kWLRxWh45D8D3Tojm45Jr4qTo4WigJ4+3blznlxg+kaa31YXQJPQw
o+XXkoDGDpZQ+mA7IxBlvoxkG6PAZ9yJU9b1tMsaXGzKcGDNbGyc7CoSyyqouTWe
9NWr+64beIA1ER7NhQIDAQAB
-----END PUBLIC KEY-----"""
Home_Node_name = "127.0.0.1:9001"

class HomeNode:
    def __init__(self,pass_phrase,port):
        self.ip = "127.0.0.1"
        self.port = port
        self.pass_phrase = pass_phrase
        self._private_key,self.public_key = self.generate_keys(pass_phrase)
        self.list_of_nodes = {}#format {'ip:port'=public_key,}
        self.mg = Message_Generator(f"{self.ip}:{self.port}",self.public_key)
                                          
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
    
    def encrypt_message(self, message, key):
        key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(key)
        encrypted = cipher.encrypt(message.encode())
        return encrypted

    def decrypt_message(self, message, key):
        key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(key)
        decrypted = cipher.decrypt(message)
        return decrypted.decode('utf-8')
    
    def verify_message(self, msg, author):
        raise NotImplementedError()

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

    def verify_signature(self, message, signature, public_key):
        key = RSA.import_key(public_key)
        h = SHA256.new(message.encode('utf-8'))
        try:
            pkcs1_15.new(key).verify(h, signature)
            return True  
        except (ValueError, TypeError, pkcs1_15.PKCS115_SigSchemeError):
            return False  
        
    async def websocket_listener(self, websocket, path):
        async for message in websocket:
            print(f"\nReceived message from WebSocket: {message}")
            await websocket.send(f"Received your message: {message}")

    async def start_server(self):
        server = await websockets.serve(self.websocket_listener, self.ip, self.port)
        await asyncio.gather(self.node_live(), server.wait_closed())

    async def node_live(self):
        while True:
            user_input = await aioconsole.ainput("Enter something (or 'quit' to exit): ")
            if user_input == 'req':
                content = self.mg.generate_message("req-join")
                encrypted_content = self.encrypt_message(content,Home_Node_Public)
                signature = self.sign_message(content,self._private_key)
                message =json.dumps( {"content":base64.b64encode(encrypted_content).decode('utf-8'),"public_key":self.public_key, "signature" : base64.b64encode(signature).decode('utf-8')})
                await self.send_message(Home_Node_name,message)
async def main():
    node = HomeNode("user2",9003)
    await node.start_server()

if __name__ == "__main__":
    asyncio.run(main())



