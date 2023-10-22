import tkinter as tk
from User_Node import User_Node
import random
import asyncio

class User_Client:
    def __init__(self, root, node: User_Node):
        self.node = node
        self.root = root
        self.root.title(f"{self.node.ip}:{self.node.port}")

        # Set the initial size of the window
        self.root.geometry("600x400")  # Adjust the size as needed

        # Create a text widget for displaying messages
        self.message_text = tk.Text(root, wrap=tk.WORD, height=15, width=40)
        self.message_text.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

        # Create buttons with empty onClick methods
        self.button1 = tk.Button(root, text="req-join", command=self.onClick1)
        self.button1.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.button2 = tk.Button(root, text="Show-My-Pub", command=self.onClick2)
        self.button2.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.button3 = tk.Button(root, text="Familiar-Nodes", command=self.onClick3)
        self.button3.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Create an exit button to close the app
        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.exit_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        
    async def run_tk(self,interval = 0.05):
            while True:
                self.root.update()
                await asyncio.sleep(interval)
        
    async def client_run(self):
         await asyncio.gather(self.node.start_server(),self.run_tk())


    def onClick1(self):
        asyncio.ensure_future(self.node.send_join_req())

    def onClick2(self):
        self.message_text.delete(1.0,tk.END)
        self.message_text.insert(tk.END, f"Public key:\n {self.node.public_key}\n\n")

    def onClick3(self):
        msg = "These are familiar nodes:\n" 
        for key in self.node.list_of_nodes.keys():
            msg+=f"{key}:\n{self.node.list_of_nodes[key]}\n"
        self.message_text.delete(1.0,tk.END)
        self.message_text.insert(tk.END, msg)



async def main():
    root = tk.Tk()
    
    random_number = random.randint(1, 99)
    node = User_Node(f"user{random_number}",9002+random_number,"127.0.0.1")

    app = User_Client(root,node)
    await app.client_run()

if __name__ == "__main__":
    asyncio.run(main())