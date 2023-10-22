from Node import Node
import json
import base64
import ast
import asyncio
import aioconsole
import random
import os
class User_Node(Node):  
    def __init__(self, pass_phrase, port, ip):
        super().__init__(pass_phrase, port, ip)

    async def analyze_message(self,message):
        msg_json = json.loads(message)
        signature = base64.b64decode(msg_json["signature"].encode('utf-8'))
        message_encrypted = msg_json["content"]

        encrypted_data = base64.b64decode(message_encrypted).decode('utf-8')
        s = ast.literal_eval(encrypted_data)
        decrypted_message = self.hybrid_decrypt(s, self._private_key)
        json_decrypted = json.loads(decrypted_message)
        if json_decrypted["type_of_message"]=="joining-list":
            nodes_to_add = json.loads(json_decrypted["content"])
            is_signature_valid = self.verify_signature(decrypted_message, signature, self.Home_Node_Public)

            if is_signature_valid:
                for key in nodes_to_add.keys():
                    self.list_of_nodes[key]=nodes_to_add[key]
            print(self.list_of_nodes)

    async def send_join_req(self):
        content = self.mg.generate_req_join(self.public_key)
        encrypted_content = self.hybrid_encrypt(content,self.Home_Node_Public)
        encrypted_data_string = base64.b64encode(str(encrypted_content).encode('utf-8')).decode('utf-8')
        signature = self.sign_message(content,self._private_key)
        message =json.dumps( {"content":encrypted_data_string, "signature" : base64.b64encode(signature).decode('utf-8')})
        await self.send_message(self.Home_Node_name,message)

    async def node_live(self):
        while True:
            user_input = await aioconsole.ainput("Enter something (or 'quit' to exit): ")
            if user_input == 'req':
                await self.send_join_req()
            if user_input == 'pub':
                print(f"{self.ip}:{self.port}")
                print(self.public_key)
            if user_input == 'clear':
                os.system('cls')
            if user_input == 'nodes':
                print(self.list_of_nodes)
async def main():
    random_number = random.randint(1, 99)
    # random_number=3
    node = User_Node(f"user{random_number}",9002+random_number,"127.0.0.1")
    
    await node.start_server()

if __name__ == "__main__":
    asyncio.run(main())



