import asyncio
import websockets

class HomeNode():
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 9001
        self.web_socket = websockets.serve(self.listen, "127.0.0.1", self.port)
        self._private_key = None
        self.public_key = None
        self.list_of_nodes = []
        self.listening_task = asyncio.create_task(self.listen(self.web_socket))
        print("Od teraz słucha")
        await self.listening_task 
    def generate_keys(self,seed):
        self.public_key, self._private_key 
        raise NotImplementedError()
    
    def verify_message(self,msg,author):
        raise NotImplementedError()
    
    async def listen(self, websocket):
        while 1:
            for message in websocket:
                print(f"Received: {message}")
            print("listening ")

             

H = HomeNode()

