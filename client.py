#client.py

import socket
import threading
import json
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import scrolledtext, ttk
import time

class ChatClient:
    def __init__(self,host='localhost',port=5555):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fernet = None
        self.username = None
        self.typing_timer = None
        self.active_users = []
        self.setup_gui()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.geometry("400x600")

        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=25)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Online users frame
        self.users_frame = ttk.LabelFrame(self.root, text="Active Users")
        self.users_frame.pack(padx=10, pady=(10, 5), fill=tk.X)  # Adding some extra padding

        # Configure the users list treeview inside the frame
        self.users_list = ttk.Treeview(self.users_frame, columns=("status",), height=10)
        self.users_list.heading("#0", text="Username")
        self.users_list.heading("status", text="Status")
        
        # Configure the column widths to avoid overlapping
        self.users_list.column("#0", width=150, anchor="center")
        self.users_list.column("status", width=100, anchor="center")

        # Adjust padding for the Treeview widget to prevent overlapping with frame borders
        self.users_list.pack(padx=15, pady=(15, 25), fill=tk.X, expand=True)

        # Adjust font size to avoid overlap
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 10))

        # Adjust padding for the treeview widget to prevent overlapping with frame borders
        self.users_list.pack(padx=15, pady=(15, 25), fill=tk.X, expand=True)

        # Message input area
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(padx=10, pady=30, fill=tk.X)

        self.message_input = ttk.Entry(self.input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_input.bind('<Key>', self.handle_typing)

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)

    def connect(self, username):
        try:
            self.socket.connect((self.host, self.port))
            self.username = username

            # Receive encryption key
            key = self.socket.recv(1024)
            self.fernet = Fernet(key)

            # Ask for preferred language
            self.preferred_language = input("Enter your preferred language for translation (e.g., 'en', 'fr', 'es'): ")
            self.socket.send(username.encode())
            self.socket.send(self.preferred_language.encode())
            self.root.title(f"Chat - {username}")

            # Start receiving messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.root.mainloop()

        except Exception as e:
            self.display_message(f"Connection error: {e}")

    def send_message(self):
        message = self.message_input.get().strip()
        if message:
            receiver = "all"  # Broadcast by default
            if message.startswith("@"):
                receiver, message = message[1:].split(" ", 1)  # For direct message

            message_data = {
                "type": "chat",
                "sender": self.username,
                "receiver": receiver,
                "content": message,
                "timestamp": time.strftime("%H:%M:%S")
            }
            self.send_encrypted_message(message_data)
            self.message_input.delete(0, tk.END)
            self.display_message(f"You ({message_data['timestamp']}): {message}")

    def handle_typing(self, event):
        if self.typing_timer:
            self.root.after_cancel(self.typing_timer)
        
        # Reset typing status after 1 second of inactivity
        self.typing_timer = self.root.after(1000, self.reset_typing_status)

    def reset_typing_status(self):
        pass

    def send_encrypted_message(self, message_data):
        message_json = json.dumps(message_data)
        encrypted_message = self.fernet.encrypt(message_json.encode())
        self.socket.send(encrypted_message)

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.socket.recv(1024)
                if not encrypted_message:
                    break
                decrypted_message = self.fernet.decrypt(encrypted_message).decode()
                message_data = json.loads(decrypted_message)
                self.handle_message(message_data)
            except Exception as e:
                self.display_message(f"Error: {e}")
                break

    def handle_message(self, message_data):
        if message_data["type"] == "chat":
            sender = message_data["sender"]
            content = message_data.get("translated_content", message_data["content"])
            self.display_message(f"{sender} ({message_data['timestamp']}): {content}")
        elif message_data["type"] == "user_list":
            self.update_active_users(message_data["active_users"])

    def display_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state=tk.DISABLED)

    def update_active_users(self, active_users):
    # Clear the current user list
        self.users_list.delete(*self.users_list.get_children())
        for user in active_users:
            self.users_list.insert("", tk.END, text=user, values=("online",))


if __name__ == "__main__":
    username = input("Enter your username: ")
    client = ChatClient()
    client.connect(username)
