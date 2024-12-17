# Multi-Client-Chat-Application

## Overview
This is a **real-time multi-client chat application** built using **Python** and **Socket Programming**. The application allows multiple users to communicate securely with features such as **private messaging**, **message encryption**, **language translation**, and **offline message support**.

## Features

- **Real-Time Messaging**:  
  The application uses **TCP/IP sockets** to enable real-time communication between clients and the server, ensuring instant message delivery.

- **Secure Messaging**:  
  All messages exchanged between clients are encrypted using **Fernet encryption** from the **Cryptography library**, ensuring privacy and security.

- **Private and Group Messaging**:  
  Users can send messages to either all connected clients (broadcast messages) or to a specific user (private messages), promoting flexible communication.

- **Language Translation**:  
  The app integrates with the **Google Translate API** to allow real-time translation of messages. Users can select their preferred language, and messages are automatically translated into it, enabling smooth communication between users speaking different languages.

- **Offline Messaging**:  
  If a recipient is offline, the server stores the message in an **SQLite** database and delivers it once the user reconnects.

- **User Authentication & Status Updates**:  
  Users authenticate using unique usernames, and their status (online/offline/typing) is displayed in real-time to all other clients.

- **Multithreading**:  
  The server uses **Python’s threading** library to handle multiple client connections concurrently, ensuring that each client can communicate independently without affecting others.

- **Graphical User Interface (GUI)**:  
  The application features a user-friendly interface built using **Tkinter**, with a chat display area, message input field, and active user list.

## Technologies Used

- **Programming Languages**:  
  - Python

- **Libraries**:  
  - **Socket Programming** (for real-time communication)  
  - **Cryptography** (for message encryption using Fernet)  
  - **Google Translate API** (for multilingual support)  
  - **SQLite** (for offline message storage)  
  - **Tkinter** (for GUI)

- **Database**:  
  - **SQLite** (for storing offline messages)

- **Networking Protocol**:  
  - **TCP/IP** for reliable communication

## How to Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/multi-client-chat-application.git
2. **Install Dependencies**:: Install the required Python libraries using pip:
   ```bash
   pip install -r requirements.txt
3. **Run the Server and the client**: Navigate to the project directory and run the server:
   ```bash
   python server.py
   python client.py
**Note**:You can open multiple terminal windows to run multiple clients.
## How It Works:
- When the client connects to the server, it sends its username and preferred language.
- The server sends an encryption key to the client.
- The client can send encrypted messages to the server, which then decrypts, processes, and either broadcasts the message to all clients or sends it to a specific recipient based on client input.
- Offline messages are stored in the SQLite database and delivered to the recipient once they reconnect.
- The user interface, built with Tkinter, provides a simple and intuitive chat window for users to interact with the system.
  **Message Format**:Provide message as "@recievername message_to_be_sent"
  **Note**: For broadcast Give message Like @all Hiii.
  This will send message i.e Hii to all the avialiable online clients
  ## Future Enhancements:
  - Add support for file sharing (images, documents, etc.)
  - Integrate voice/video calling features.
  - Support for group chats.
  - Improve language translation using AI-based models.
  - Enhance offline message synchronization across multiple devices.
  - Move to a more scalable database like PostgreSQL for better performance.
  ## Acknowledgments:
  - **Python**: For its simplicity and power in building this application.
  - **Cryptography**: For providing robust encryption for secure messaging.
  - **Google Translate API**: For enabling real-time translation.
  - **Tkinter**: For building the graphical user interface. 
  

