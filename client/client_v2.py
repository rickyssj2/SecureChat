import websockets
import aioconsole
import asyncio
import hashlib
import base64
import uuid
from rsa_encryption_util import RSAEncryptionUtil
import json

async def check_target_presence(websocket, target_username):
    # Request presence status of the target user
    print('Checking target presence...')
    await websocket.send(json.dumps({
        'action': 'check_presence',
        'target_username': target_username
    }))
    
    # Receive and parse the response from the server
    response_json = await websocket.recv()
    response = json.loads(response_json)
    
    # Extract the presence information
    is_target_user_active = response.get('is_active', False)
    target_user_public_key = response.get('public_key')
    
    print(f"Presence response: {response}")
    print(f"Target user public key: {target_user_public_key if target_user_public_key else 'Unavailable'}")
    
    # Return target details
    return is_target_user_active, target_user_public_key

async def register_client(websocket, client_id, client_public_key):
    # Send registration message with client_id and public key
    await websocket.send(json.dumps({
        'action': 'register_client',
        'client_id': client_id,
        'public_key': client_public_key
    }))

async def register_user(websocket):
    await websocket.send("register") #TODO: Build a simple protocol for each event
    while True:      
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        password_hash = hashlib.sha256(password.encode()).hexdigest() # Not storing password directly; collision is unlikely
        await websocket.send(f"{username},{password_hash}") #TODO: Build a simple protocol for each event
        response = await websocket.recv() #TODO: Build a simple protocol for each event
        if response == "Username already taken. Please try another one.":
            print(response)
            continue                    
        break
    return True

async def authenticate_user(websocket):
    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        # Repeated code in register and login, create a function
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        await websocket.send(f"{username},{password_hash}")
        auth_response = await websocket.recv()
        if auth_response != "Authentication successful":
            print('Authenticaltion Failed! Try again.')
            continue
        break
    return True 

async def send_messages(websocket, target_username, target_user_public_key, rsa_util):
    while True:
        message = await aioconsole.ainput("You: ")  # Asynchronous input
        public_key = RSAEncryptionUtil.load_public_key(target_user_public_key)
        encrypted_message = rsa_util.encrypt(message, public_key)
        base64_encrypted_message = base64.b64encode(encrypted_message).decode('utf-8')
        await websocket.send(json.dumps({
            'action': 'send_encrypted_message',
            'target_username': target_username,
            'message': base64_encrypted_message
        }))

async def receive_messages(websocket, rsa_util):
    while True:
        response_json = await websocket.recv()
        response_data = json.loads(response_json)
        # Get the Base64-encoded message
        encrypted_message_base64 = response_data['message']
        # Decode the Base64 string back to bytes
        encrypted_message_bytes = base64.b64decode(encrypted_message_base64)
        # Decrypt the message with the recipient's private key
        decrypted_message = rsa_util.decrypt(encrypted_message_bytes)
        print(f"\r{' ' * 50}\rOther: {decrypted_message}")  # Clear the line and print the message
        # Reprint the input prompt
        print("You: ", end='', flush=True)

async def chat_client(client_id):
    #TODO: Define configuration in ENV variables
    uri = "ws://localhost:6789"
    rsa_util = RSAEncryptionUtil()
    client_public_key = rsa_util.get_public_key_bytes().decode('utf-8')
    async with websockets.connect(uri) as websocket:
        isAuthenticated = False
        # Register with client_id and public key
        await register_client(websocket, client_id, client_public_key)
        print("Connected to the chat server!")
        
        while True:
            # Choose action: register or login
            action = input("Type 'register' to create a new account or 'login' to access an existing one: ").strip().lower()
            if action == 'register':
                isAuthenticated = await register_user(websocket)
            
            # For login
            elif action == 'login':
                isAuthenticated = await authenticate_user(websocket)

            while isAuthenticated:
                target_username = input("Enter your friend's username to start chatting: ")
                
                # Check if target user is active
                while True:
                    # Create the check presence task
                    is_target_user_active, target_user_public_key = await check_target_presence(websocket, target_username)
                    
                    if is_target_user_active and target_user_public_key:
                        print(f"User '{target_username}' is online. Starting chat...")
                        
                        # Start sending and receiving messages concurrently
                        send_task = asyncio.create_task(send_messages(websocket, target_username, target_user_public_key, rsa_util))
                        receive_task = asyncio.create_task(receive_messages(websocket, rsa_util))
                        
                        # Wait for both tasks to finish
                        await asyncio.gather(send_task, receive_task)
                        break  # Exit the presence check loop once chatting starts
                    else:
                        print(f"User '{target_username}' is not available. Checking again in a moment...")
                        await asyncio.sleep(3)  # Wait before checking again

if __name__ == "__main__":
    client_id = str(uuid.uuid4())  # Generate a random UUID as client ID
    asyncio.run(chat_client(client_id))
