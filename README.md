# 🛡️ SecureChat: End-to-End Encrypted Chat Application

A highly scalable, distributed, and end-to-end encrypted chat application built with WebSockets and RSA encryption in Python. This application ensures **end-to-end encryption** (E2EE) for all messages, where only the intended recipients can decrypt messages, leaving intermediaries (message-brokers) unable to view the contents.

## 📜 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Setup](#-setup)
- [Usage](#-usage)
- [Folder Structure](#-folder-structure)
- [Dependencies](#-dependencies)
- [Contributing](#-contributing)

---

## ✨ Features

- **End-to-End Encryption**: Messages are encrypted with RSA and can only be decrypted by the intended recipient.
- **User Registration & Authentication**: Users register with a username and password, with hashed password storage. Credentials are store in SQLite DB.
- **Presence Check**: Clients can check if a target user is online before a user can start sending messages.
- **Scalable WebSocket-Based Communication**: Real-time message delivery over WebSockets.

---

## 🏛️ Architecture

The application follows a client-server architecture, with the server managing connected clients and relaying encrypted messages. Below is an overview of how the application components interact:

### 1. **Client** 💻
   - Registers with the server and authenticates using a username and password.
   - Generates an RSA key pair locally (public key shared with the server; private key kept secure).
   - Requests the public key of the target client from the server.
   - Encrypts messages using the target client’s public key, ensuring end-to-end security.
   - Decrypts incoming messages using its own private key.

### 2. **Server** 🖥️
   - Manages WebSocket connections and client authentication.
   - Stores client public keys and client statuses.
   - Responds to clients with the requested public key of a target client.
   - Forwards encrypted messages to the target client without decrypting them.

> **Note**: The server only stores the public keys and handles message transmission; it cannot decrypt messages.

---

## 🚀 Setup

### Prerequisites

- Python 3.8+
- `pip` (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rickyssj2/SecureChat.git
   cd SecureChat
2. Install the required packages:
   ```bash
   pip install client/requirements.txt
   pip install server/requirements.txt
3. Run the server
    ```bash
    python3 server/server_v2.py
4. Run the client
    ```bash
    python3 client/client_v2.py
5. Follow the steps to start chatting

## 📖 Usage
 - Register or Login: When the client starts, choose to register a new account or login with existing credentials.
 - Initiate Chat: Enter the target username you want to connect with. The server will confirm if the user is online and provide their public key if available.
 - Start Messaging: Begin exchanging encrypted messages with your friend. Messages will be encrypted locally by the sender and decrypted by the recipient, ensuring complete security.

## 📂 Folder Structure
encrypted-chat-app/
├── client                   
│      ├── client_v2.py             # Client script
│      ├── rsa_encryption_util.py   # RSA utility for encryption/decryption
│      ├── ... other versions       # v0 to v1.2 are incremental clients built for prototyping
│      └── requirements.txt         # Python dependencies for client
├── server                
│      ├── server_v2.py             # Server script
│      ├── ... other versions       # v0 to v1.1 are incremental clients built for prototyping
│      └── requirements.txt         # Python dependencies for server
└── README.md                # Project documentation

## 📦 Dependencies
 - asyncio: Provides asynchronous I/O operations.
 - websockets: Enables WebSocket communication between clients and server.
 - rsa: Provides RSA encryption and decryption capabilities.
 - hashlib: Supports hashing for password security.
 - uuid: Generates unique identifiers for clients.
 - aioconsole: Supports asynchronous console input for a better user experience.
 - sqlite: Used for lightweight data storage, such as user information and public keys.

Install all dependencies by running
    ```bash
    pip install -r client/requirements.txt
    pip install -r server/requirements.txt

## 🤝 Contributing
Contributions are welcome! Feel free to submit a pull request to suggest improvements, fix bugs, or add features.

 - Fork the repository.
 - Create a new branch (git checkout -b feature/YourFeature).
 - Commit your changes (git commit -am 'Add new feature').
 - Push to the branch (git push origin feature/YourFeature).
 - Create a new Pull Request.




