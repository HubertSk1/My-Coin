import json 
    
class Message_Generator:
    def __init__(self,author,pub_key):
        self.possible_types = ["req-join"]
        self.author = author #ip:port
        self.public_key = pub_key
    
    def generate_message(self, type_of_message):
        if type_of_message not in self.possible_types:
            raise Exception("Wrong Message type, restart")
        if type_of_message == "req-join":
            message = {"author": self.author,"type_of_message":"req-join", "content" : ""}
            msg = json.dumps(message)
            return msg
        




        
