import asyncio
import websockets
import sqlite3
import rsa
import base64
import hashlib

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def fetch_user_from_db(username, conn):
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()
    return existing_user

def insert_user_in_db(username, password, conn):
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password))
    conn.commit()
# Store active clients & connected users
active_clients = {}
connected_users = {}

async def register_user(websocket):
    registration_data = await websocket.recv()
    username, password = registration_data.split(',')

    conn = sqlite3.connect('users.db')
    existing_user = fetch_user_from_db(username, conn)

    if existing_user:
        await websocket.send("Username already taken. Please try another one.")
    else:
        insert_user_in_db(username, password, conn)
        await websocket.send("Registration successful. You can now log in.")
    
    conn.close()
    return username  # Return the username for further actions

def associate_user_with_client_id(username, client_id):
    connected_users[username] = client_id
    return

async def authenticate(websocket):
    while True:
        auth_data = await websocket.recv()
        # TODO: move to a separate function
        if auth_data.startswith("register"):
            username = await register_user(websocket)
            return username  # Return username for subsequent actions

        # Check if username already exists
        username, password = auth_data.split(',')
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()

        if row and password == row[0]:
            await websocket.send("Authentication successful")
            return username
        else:
            await websocket.send("Authentication failed, please try again or register.")

async def handle_client(websocket, path):
    # Register a new client
    client_id = await websocket.recv()
    active_clients[client_id] = websocket
    print(f"Client {client_id} connected.")

    # Authenticate user
    username = await authenticate(websocket)
    # TODO: users can connect with multiple devices, change data structure
    associate_user_with_client_id(username, client_id)
    print(f"{username} connected successfully!")

    # try:
    #     while True:
    #         target_user = await websocket.recv()
    #         if target_user in connected_users:
    #             # Send public keys
    #             # TODO: server will not generate keys, only clients will
    #             user_public_key = rsa.newkeys(512)[0].save_pkcs1(format='PEM')
    #             target_client = connected_users[target_user]
    #             target_websocket = active_clients[target_client]

    #             await websocket.send(base64.b64encode(user_public_key).decode())
    #             target_websocket.send(base64.b64encode(user_public_key).decode())

    #             # Chat loop
    #             while True:
    #                 message = await websocket.recv()
    #                 encrypted_message = rsa.encrypt(message.encode('utf-8'), target_websocket.public_key)
    #                 await target_websocket.send(encrypted_message)
    #         else:
    #             await websocket.send("Target user not found.")
    # except websockets.exceptions.ConnectionClosed:
    #     print(f"Client {client_id} disconnected.")
    # finally:
    #     del connected_users[client_id]
    try:
        print("Waiting for messages ...")
        print(f"Current websocket: {websocket}")
        async for message in websocket:

            print(f"Received message from {username}")
            # Broadcast the received message to all connected clients
            for client in active_clients:
                if active_clients[client] != websocket:  # Don't send the message back to the sender
                    await active_clients[client].send(message)
    finally:
        # Unregister the client when done
        del active_clients[client_id]

async def main():
    server = await websockets.serve(handle_client, "localhost", 6789)
    print("WebSocket server started on ws://localhost:6789")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
