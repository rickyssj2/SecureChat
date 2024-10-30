import asyncio
import websockets
import rsa
import base64
import hashlib
import uuid

async def chat_client(client_id):
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
                    registration_data = input("Enter your username and password in the format: username,password: ")
                    await websocket.send(registration_data)
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
                await websocket.send(f"{username},{password}")
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
                    if response == "Target user not found.":
                        print("Target user not found. The user is either inactive or no such user exists")
                        continue
                    break
                # Receive public key
                public_key_data = await websocket.recv()
                public_key = rsa.PublicKey.load_pkcs1(base64.b64decode(public_key_data))

                while True:
                    message = input("Type your message (or 'exit' to quit): ")
                    if message.lower() == 'exit':
                        break
                    encrypted_message = rsa.encrypt(message.encode('utf-8'), public_key)
                    await websocket.send(encrypted_message)

if __name__ == "__main__":
    client_id = str(uuid.uuid4())  # Generate a random UUID as client ID
    asyncio.run(chat_client(client_id))
