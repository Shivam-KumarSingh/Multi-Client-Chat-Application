#Server.py
import socket
import threading
import sqlite3
import json
from cryptography.fernet import Fernet
from googletrans import Translator
import time  # Add this import for timestamps

class ChatServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {client_socket: {"username": str, "key": bytes, "language": str}}
        self.active_users = set()
        self.message_queue = sqlite3.connect('messages.db', check_same_thread=False)
        self.message_queue.execute('''CREATE TABLE IF NOT EXISTS messages
                                      (sender TEXT, receiver TEXT, message TEXT, timestamp TEXT)''')
        self.translator = Translator()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()
            print(f"New client connected from {address}")
            threading.Thread(target=self.handle_client,args=(client_socket,)).start()

    def handle_client(self, client_socket):
        username,key,language = self.handle_client_setup(client_socket)
        if not username:
            return

        self.broadcast_user_list()
        try:
            self.send_offline_messages(username,client_socket)
            while True:
                encrypted_message = client_socket.recv(1024)
                if not encrypted_message:
                    break

                sender_username = self.clients[client_socket]["username"]
                message_data = self.process_message(encrypted_message, key)

                if message_data["type"] == "chat":
                    if message_data["receiver"] == "all":
                        self.broadcast_message(sender_username, message_data["content"])
                    else:
                        self.send_direct_message(sender_username, message_data["receiver"], message_data["content"])

                    self.store_offline_message(sender_username, message_data["receiver"], message_data["content"])

        except Exception as e:
            print(f"Error handling client {username}: {e}")
        finally:
            self.handle_client_disconnect(client_socket)

    def handle_client_setup(self, client_socket):
        try:
            key = Fernet.generate_key()
            client_socket.send(key)
            username = client_socket.recv(1024).decode()
            language = client_socket.recv(1024).decode()
            self.clients[client_socket] = {"username": username, "key": key, "language": language}
            self.active_users.add(username)
            print(f"{username} has joined the chat with preferred language {language}")
            return username, key, language
        except:
            client_socket.close()
            return None, None, None

    def process_message(self, encrypted_message, key):
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message).decode()
        return json.loads(decrypted_message)

    def broadcast_message(self, sender, content):
        for client_socket, client_info in self.clients.items():
            if client_info["username"] != sender:
                translated_content = self.translate_message(content, client_info["language"])
                self.send_message(client_socket, {
                    "type": "chat",
                    "sender": sender,
                    "content": translated_content,
                    "timestamp": time.strftime("%H:%M:%S")
                })

    def send_direct_message(self, sender, receiver, content):
        for client_socket, client_info in self.clients.items():
            if client_info["username"] == receiver:
                translated_content = self.translate_message(content, client_info["language"])
                self.send_message(client_socket, {
                    "type": "chat",
                    "sender": sender,
                    "content": translated_content,
                    "timestamp": time.strftime("%H:%M:%S")
                })
                return  # Only send once if user is found

    def send_message(self, client_socket, message_data):
        key = self.clients[client_socket]["key"]
        f = Fernet(key)
        encrypted_message = f.encrypt(json.dumps(message_data).encode())
        client_socket.send(encrypted_message)

    def store_offline_message(self, sender, receiver, message):
        self.message_queue.execute("INSERT INTO messages (sender, receiver, message, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (sender, receiver, message))
        self.message_queue.commit()

    def send_offline_messages(self, username, client_socket):
        cursor = self.message_queue.execute("SELECT sender, message, timestamp FROM messages WHERE receiver = ?", (username,))
        for sender, message, timestamp in cursor:
            self.send_message(client_socket, {
                "type": "chat",
                "sender": sender,
                "content": message,
                "timestamp": timestamp
            })
        self.message_queue.execute("DELETE FROM messages WHERE receiver = ?", (username,))
        self.message_queue.commit()

    def handle_client_disconnect(self, client_socket):
        if client_socket in self.clients:
            username = self.clients[client_socket]["username"]
            self.active_users.discard(username)
            del self.clients[client_socket]
            print(f"{username} has left the chat.")
            self.broadcast_user_list()
        client_socket.close()

    def broadcast_user_list(self):
        active_user_list = list(self.active_users)
        for client_socket in self.clients:
            self.send_message(client_socket, {
                "type": "user_list",
                "active_users": active_user_list
            })

    def translate_message(self, message, target_lang):
        translation = self.translator.translate(message, dest=target_lang)
        return translation.text


if __name__ == "__main__":
    server = ChatServer()
    server.start()
