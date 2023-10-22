import json 
    
class Message_Generator:
    def __init__(self,author,pub_key):
        self.possible_types = ["req-join"]
        self.author = author #ip:port
        self.public_key = pub_key
    
    def generate_req_join(self,public_key):
        message = {"author": self.author, "public_key":public_key, "type_of_message":"req-join"}
        msg = json.dumps(message)
        return msg
    def generate_joining_list(self,list_of_nodes_json):
        message = {"author": self.author, "type_of_message":"joining-list", "content" : json.dumps(list_of_nodes_json)}
        msg = json.dumps(message)
        return msg
        



        
