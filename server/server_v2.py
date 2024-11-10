import asyncio
import websockets
import sqlite3
import json

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

async def check_presence(websocket, target_username, username):
    # Is target user active check
    is_active = False  
    if target_username in connected_users and target_username != username:
        is_active = True
    target_user_public_key = None
    if is_active:
        target_user_client_id = connected_users[target_username]
        target_user_public_key = active_clients[target_user_client_id]['public_key']
    await websocket.send(json.dumps({
        'action': 'check_presence_response',
        'is_active': is_active,
        'public_key': target_user_public_key
    }))
    return target_username

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
    # Initiate encryption before sending any messages
    client_init_json = await websocket.recv()
    client_init_data = json.loads(client_init_json)
    client_id = client_init_data['client_id']
    # Register a new client
    if client_init_data['action'] == 'register_client':        
        client_public_key = client_init_data['public_key']
        active_clients[client_id] = {
            'websocket': websocket,
            'public_key': client_public_key
        }
        print(f"Client {client_id} connected.")

    # Authenticate user
    username = await authenticate(websocket)
    # TODO: users can connect with multiple devices, change data structure
    associate_user_with_client_id(username, client_id)
    print(f"{username} connected successfully!")

    try:
        print("Waiting for messages ...")
        async for message in websocket:
            data = json.loads(message)

            if data['action'] == 'check_presence':
                target_username = data['target_username']
                await check_presence(websocket, target_username, username)
            elif data['action'] == 'send_encrypted_message':
                print(f"Received message from {username}")
                # Send message to target_username
                if target_username in connected_users:
                    client_id = connected_users[target_username]
                    current_client = active_clients[client_id]
                    await current_client['websocket'].send(message)
    finally:
        # Unregister the client when done
        del connected_users[username]
        del active_clients[client_id]

async def main():
    server = await websockets.serve(handle_client, "localhost", 6789)
    print("WebSocket server started on ws://localhost:6789")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
