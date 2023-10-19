import asyncio
import websockets
import aioconsole
import hashlib
from Crypto.PublicKey import RSA
from Crypto import Random
import hashlib
from Crypto.Cipher import PKCS1_OAEP

class HomeNode:
    def __init__(self,pass_phrase):
        self.ip = "127.0.0.1"
        self.port = 9001
        self.pass_phrase = pass_phrase
        self._private_key,self.public_key = self.generate_keys(pass_phrase)
        self.list_of_nodes = {}#format {'ip:port'=public_key,}
    
    def generate_keys(self, input_word: str) -> (str, str):
        """Derive a private and public key pair from the user input using PBKDF2."""
        seed = hashlib.sha256(input_word.encode('utf-8')).digest()
        random_generator = Random.new(seed).read
        key = RSA.generate(1024, random_generator) 
        private_key=key.export_key().decode('utf-8')
        public_key = key.publickey().export_key().decode('utf-8') 
        return (private_key ,public_key)
    
    def encrypt_message(self,message,key):
        key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(key)
        encrypted = cipher.encrypt(message.encode())
        return encrypted
    
    def decrypt_message(self,message,key):
        key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(key)
        decrypted = cipher.decrypt(message)
        return decrypted
    
    def verify_message(self, msg, author):
        raise NotImplementedError()

    async def websocket_listener(self, websocket, path):
        async for message in websocket:
            print(f"\nReceived message from WebSocket: {message}")
            await websocket.send(f"Received your message: {message}")

    async def node_live(self):
        while True:
            user_input = await aioconsole.ainput("Enter something (or 'quit' to exit): ")
            if user_input == 'quit':
                break
            print(f"You entered: {user_input}")

    async def start_server(self):
        server = await websockets.serve(self.websocket_listener, self.ip, self.port)
        await asyncio.gather(self.node_live(), server.wait_closed())

    async def send_message(name,message): #name format ip:port
        uri = f"ws://{name}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)
            await websocket.close()

# Create an instance of HomeNode and start the server
async def main():
    node = HomeNode("papa")
    await node.start_server()

if __name__ == "__main__":
    asyncio.run(main())


message = {'name':"" , "message": "", "Signature" : {} }