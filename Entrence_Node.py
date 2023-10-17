import asyncio
import websockets
import aioconsole
class HomeNode():

    async def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 9001
        self.web_socket = websockets.serve(self.listen, "127.0.0.1", self.port)
        self._private_key = None
        self.public_key = None
        self.list_of_nodes = []
        self.server = await websockets.serve(self.websocket_listener, '127.0.0.1', 9001)
        await asyncio.gather(self.node_live(), self.server.wait_closed())
        
    def generate_keys(self,seed):
        self.public_key, self._private_key 
        raise NotImplementedError()
    
    def verify_message(self,msg,author):
        raise NotImplementedError()
    
    async def websocket_listener(websocket, path):
        async for message in websocket:
            print(f"\nReceived message from WebSocket: {message}")
            await websocket.send(f"Received your message: {message}")
    
    async def node_live():
        while True:
            user_input = await aioconsole.ainput("Enter something (or 'quit' to exit): ")
            if user_input == 'quit':
                break
            print(f"You entered: {user_input}")

HomeNode()