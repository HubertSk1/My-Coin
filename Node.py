from websocket_server import WebsocketServer
import websocket
import random 
import json
import hashlib
import base64
import threading
import os,sys
import random
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes


from Message import Message_Generator
from block import BlockChain

class Node:
    def __init__(self,pass_phrase,port,ip):
        self.ip = ip
        self.port = port
        self.pass_phrase = pass_phrase
        
        self._private_key, self.public_key = self.generate_keys(pass_phrase)
        self.mg = Message_Generator(f"{self.ip}:{self.port}",self.public_key)
        self.Home_Node_Public = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCRmK3JDQObgn+RKUSbo5zzvazu
NZ7QP/fx7T4kWLRxWh45D8D3Tojm45Jr4qTo4WigJ4+3blznlxg+kaa31YXQJPQw
o+XXkoDGDpZQ+mA7IxBlvoxkG6PAZ9yJU9b1tMsaXGzKcGDNbGyc7CoSyyqouTWe
9NWr+64beIA1ER7NhQIDAQAB
-----END PUBLIC KEY-----"""
        self.Home_Node_name = "127.0.0.1:9001"
        self.list_of_nodes = {self.Home_Node_Public:self.Home_Node_name} #format {public_key":"ip:port"}

        #BLOCKCHAIN
        self.blockchain = BlockChain(5)
        self.block_chain_edited_event = threading.Event()
        self.start_mining = threading.Event()

    #SIGNATURES
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
    
    def sign_message(self, message, private_key):
        key = RSA.import_key(private_key)
        if type(message) ==bytes:
            h = SHA256.new(message)
        else:    
            h = SHA256.new(message.encode('utf-8'))
        signature = pkcs1_15.new(key).sign(h)
        return signature

    def verify_signature(self,message, signature, public_key):
        key = RSA.import_key(public_key)
        h = SHA256.new(message.encode('utf-8'))
        try:
            pkcs1_15.new(key).verify(h, signature)
            return True  
        except Exception:
            return False
    
    def start_miner(self):
        while 1:
            if self.start_mining.is_set():
                self.block_chain_edited_event.clear()
                found, new_block = self.blockchain.generate_next_block("",self.block_chain_edited_event)
                if found:
                    self.blockchain.add_block(new_block)
                    self.send_synchro_blockchain()
                    self.start_mining.clear()

    def start_server(self):
        receive_thread = threading.Thread(target = self.start_listener,daemon=True)
        send_thread = threading.Thread(target = self.live)
        mine_thread = threading.Thread(target = self.start_miner,daemon=True)
        receive_thread.start()
        send_thread.start()
        mine_thread.start()

    #SERVER SENDING MESSAGES
    def send_msg(self, name, message):
        for_signing = json.dumps(message)
        signature = self.sign_message(for_signing, self._private_key)
        signature = base64.b64encode(signature).decode('utf-8')
        
        msg_to_send = {"signature":signature, "content":message}
        msg_json = json.dumps(msg_to_send)
        uri = f"ws://{name}" #ip:port
        ws = websocket.WebSocket()
        ws.connect(uri)
        try:
            ws.send(msg_json)

        finally:
            ws.close()

    def send_familiar_nodes(self,target_node_name):
        key_value_list = self.list_of_nodes.keys()
        if len(key_value_list) < 3:
            selected_data = self.list_of_nodes
        else:
            key_value_list = random.sample(key_value_list, 3)
            selected_data = {field: self.list_of_nodes[field] for field in key_value_list if self.list_of_nodes[field] != target_node_name}
        selected_data = {"nodes":selected_data,"blockchain":self.blockchain.pack_blockchain()}
        data = json.dumps(selected_data)
        message = self.mg.generate_message("join-list",data)
        self.send_msg(target_node_name, message)

    
    def send_request_join(self):
        message = self.mg.generate_message("req-join",None)
        self.send_msg(self.Home_Node_name,message)

    def send_synchro_blockchain(self,to_skip=None):
        message =self.mg.generate_message("blockchain-sync",{"blockchain": self.blockchain.pack_blockchain()})
        for name in self.list_of_nodes.values():
            if name != to_skip:
                self.send_msg(name,message)

    #SERVER RECEIVING MESSAGES
    def start_listener(self):
        server = WebsocketServer(port=self.port)  # You can specify your desired port

        server.set_fn_message_received(self.analyze_message)
        try:
            server.run_forever()
        except KeyboardInterrupt:
            print("Server stopping...")
            server.shutdown() 
        server.run_forever()


    def analyze_message(self,client, server, message):
        msg_json = json.loads(message)
        content = msg_json["content"]
        signature = base64.b64decode(msg_json["signature"].encode('utf-8'))
        if self.verify_signature(json.dumps(content),signature,content["public_key"]):
            if content['author']==f"{self.ip}:{self.port}":
                print("self_message_ignored")
                return None
            msg_type = content["message_type"]

            if msg_type == "req-join":
                self.send_familiar_nodes(content['author'])
                self.list_of_nodes[content["public_key"]]=content["author"]
                print("got reqeust-join, send join-list")
            
            elif msg_type == "join-list":
                print("got_node_list")
                data = json.loads(content["data"])
                nodes = data["nodes"]  
                for key,value in nodes.items():
                    self.list_of_nodes[key] = value
                try:
                    self.list_of_nodes.pop(self.public_key)
                except:
                    pass
                blockchain_to_check = BlockChain.unpack_blockchain(data["blockchain"].encode("latin-1"))
                self.blockchain.find_longer_chain(blockchain_to_check)

            elif msg_type == "blockchain-sync" :
                data = content["data"]
                name = content["author"]
                print(f"got sync from {name}")
                blockchain_to_check = BlockChain.unpack_blockchain(data["blockchain"].encode("latin-1"))
                if self.blockchain.find_longer_chain(blockchain_to_check):
                    self.send_synchro_blockchain(name)
                

    # UI        
    def live(self):
        while 1:
            try:
                user_input = input("input ur command here:\n")
            except KeyboardInterrupt:
                N.receive_thread.join()  # Optionally join threads to ensure they have stopped
                N.send_thread.join()
                print("Exiting...")
                break
            except EOFError:
                break
            if user_input == 'req':
                self.send_request_join()
            elif user_input == 'pub':
                print(f"{self.ip}:{self.port}")
                print(self.public_key)
            elif user_input == 'clear':
                os.system('cls')
            elif user_input == 'nodes':
                print(self.list_of_nodes)
            elif user_input == 'blockchain':
                [print(f"-----\n{block}\n-----") for block in self.blockchain.chain]
            elif user_input == 'mine':
                self.start_mining.set()
            #TEST
            elif user_input == 'change':
                self.block_chain_edited_event.set()
        sys.exit()

if __name__ == "__main__":
    random_number = random.randint(1, 99)
    N = Node(f"user{random_number}",9001+random_number,"127.0.0.1")
    N.start_server()