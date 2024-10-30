# SecureChat
Highly scalable, distributed, and end-to-end encrypted chat application built in Python.

This is a simple chat application that allows users to communicate securely using WebSockets. It supports user authentication, public key exchange, and encrypted messages.

## Features

- User registration with a username and password
- Secure communication using RSA encryption
- Direct public key exchange between clients
- SQLite database for user management

## Requirements

- Python 3.x
- `websockets`
- `rsa`
- `hashlib`
- `sqlite3`

## Installation

1. Clone the repository or download the source code.
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

