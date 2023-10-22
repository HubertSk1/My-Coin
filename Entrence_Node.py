import asyncio
import aioconsole
import json
import base64
from Crypto.Random import get_random_bytes
import ast
from Node import Node
import random
class HomeNode(Node):
    def __init__(self):
        super().__init__("home",9001,"127.0.0.1")

    async def send_joining_list(self,receiver_name):
        key_value_list = list(self.list_of_nodes.keys())

        if len(key_value_list) < 2:
            key_value_list = None
            selected_data={}
        else:
            key_value_list = random.sample(key_value_list, 2)
            selected_data = {field: self.list_of_nodes[field] for field in key_value_list if field != receiver_name}
        
        content = self.mg.generate_joining_list(selected_data)
        encrypted_content = self.hybrid_encrypt(content,self.list_of_nodes[receiver_name])
        encrypted_data_string = base64.b64encode(str(encrypted_content).encode('utf-8')).decode('utf-8')
        signature = self.sign_message(content,self._private_key)
        message =json.dumps( {"content":encrypted_data_string, "signature" : base64.b64encode(signature).decode('utf-8')})
        await self.send_message(receiver_name,message)

    async def analyze_message(self,message):
        msg_json = json.loads(message)
        signature = base64.b64decode(msg_json["signature"].encode('utf-8'))
        message_encrypted = msg_json["content"]

        encrypted_data = base64.b64decode(message_encrypted).decode('utf-8')
        s = ast.literal_eval(encrypted_data)
        decrypted_message = self.hybrid_decrypt(s, self._private_key)
        json_decrypted = json.loads(decrypted_message)

        if json_decrypted["type_of_message"]=="req-join":
            is_signature_valid = self.verify_signature(decrypted_message, signature, json_decrypted["public_key"])
            if is_signature_valid:
                self.list_of_nodes[json_decrypted["author"]]=json_decrypted["public_key"]
                
                await self.send_joining_list(json_decrypted["author"])

    async def node_live(self):
        while True:
            user_input = await aioconsole.ainput("Enter_Home_Node_Commends:\n")
            if user_input == 'quit':
                break
            print(f"You entered: {user_input}")

async def main():
    node = HomeNode()
    await node.start_server()

if __name__ == "__main__":
    asyncio.run(main())

