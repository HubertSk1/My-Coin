# class Home_Node():
#     def __init__(self):
#         self.ip = "127.0.0.2"
#         self.port = 9001
#         self._private_key = None
#         self.public_key = None
    
#     def generate_keys(self,seed):
#         self.public_key, self._private_key 
#         raise NotImplementedError()
    
#     def verify_message(self,msg,author):
#         raise NotImplementedError()

import asyncio
import websockets

async def echo_client():
    uri = "ws://localhost:9001"
    async with websockets.connect(uri) as websocket:
        while True:
            message = input("Enter a message: ")
            await websocket.send(message)
            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.get_event_loop().run_until_complete(echo_client())
