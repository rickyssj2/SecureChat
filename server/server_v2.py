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

# Store active clients
active_clients = {}

async def register_user(websocket):
    registration_data = await websocket.recv()
    username, password = registration_data.split(',')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        await websocket.send("Username already taken. Please try another one.")
    else:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        await websocket.send("Registration successful. You can now log in.")
    
    conn.close()
    return username  # Return the username for further actions

async def authenticate(websocket):
    while True:
        auth_data = await websocket.recv()
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

        if row and hashlib.sha256(password.encode()).hexdigest() == row[0]:
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
    print(f"{username} connected successfully!")

    try:
        while True:
            target_user = await websocket.recv()
            if target_user in active_clients:
                # Send public keys
                user_public_key = rsa.newkeys(512)[0].save_pkcs1(format='PEM')
                target_websocket = active_clients[target_user]

                await websocket.send(base64.b64encode(user_public_key).decode())
                target_websocket.send(base64.b64encode(user_public_key).decode())

                # Chat loop
                while True:
                    message = await websocket.recv()
                    encrypted_message = rsa.encrypt(message.encode('utf-8'), target_websocket.public_key)
                    await target_websocket.send(encrypted_message)
            else:
                await websocket.send("Target user not found.")
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_id} disconnected.")
    finally:
        del active_clients[client_id]

async def main():
    server = await websockets.serve(handle_client, "localhost", 6789)
    print("WebSocket server started on ws://localhost:6789")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
