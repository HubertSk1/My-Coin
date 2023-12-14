import json
from typing import Any 
    
class Message_Generator:
    def __init__(self,author,pub_key):
        self.possible_types = ["req-join"]
        self.author = author #ip:port
        self.public_key = pub_key
    
    def generate_message(self, message_type:str, data: Any =None):
        msg = {"public_key":self.public_key,"author":self.author,"message_type":message_type, "data":data}
        return msg