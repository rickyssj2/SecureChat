import asyncio
import websockets
import rsa
import base64
import hashlib
import uuid

async def chat_client(client_id):
    #TODO: Define configuration in ENV variables
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        isConnected = False
        await websocket.send(client_id)
        while True:
            # Choose action: register or login
            action = input("Type 'register' to create a new account or 'login' to access an existing one: ").strip().lower()
            if action == 'register':
                await websocket.send("register")
                while True:      
                    username = input("Enter your username: ")
                    password = input("Enter your password: ")
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    await websocket.send(f"{username},{password_hash}")
                    response = await websocket.recv()
                    if response == "Username already taken. Please try another one.":
                        print(response)
                        continue                    
                    isConnected = True
                    break
            
            # For login
            elif action == 'login':
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                await websocket.send(f"{username},{password_hash}")
                auth_response = await websocket.recv()
                print(auth_response)

                if auth_response != "Authentication successful":
                    print('Authenticaltion Failed! Try again.')
                    isConnected = False
                    continue
                isConnected = True                

            # Select target user
            if isConnected:
                while True:
                    target_user = input("Enter the username of the client you want to chat with: ")
                    await websocket.send(target_user)
                    response = await websocket.recv()
                    #TODO: Try to build a protocol and a parser instead of sending strings,  OR atleast use error codes
                    if response == "Target user not found.":
                        print("Target user not found. The user is either inactive or no such user exists")
                        continue
                    break
                # TODO: Send encrypted messages to the server from the start
                # TODO: Don't ask for the server to send public keys, the initiator would send it's puclic keys
                # Receive public key
                public_key_data = await websocket.recv()
                public_key = rsa.PublicKey.load_pkcs1(base64.b64decode(public_key_data))

                while True:
                    message = input("Type your message (or 'exit' to quit): ")
                    if message.lower() == 'exit':
                        break
                    # TODO: Use RSA for sharing AES256 keys, symmetric encryption is faster and more compute efficient
                    encrypted_message = rsa.encrypt(message.encode('utf-8'), public_key)
                    await websocket.send(encrypted_message)

if __name__ == "__main__":
    client_id = str(uuid.uuid4())  # Generate a random UUID as client ID
    asyncio.run(chat_client(client_id))
