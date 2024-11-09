import websockets
import aioconsole
import asyncio
import hashlib
import uuid

async def send_messages(websocket):
    while True:
        message = await aioconsole.ainput("You: ")  # Asynchronous input
        await websocket.send(message)

async def receive_messages(websocket):
    while True:
        response = await websocket.recv()
        print(f"\r{' ' * 50}\rOther: {response}")  # Clear the line and print the message
        # Reprint the input prompt
        print("You: ", end='', flush=True)

async def chat_client(client_id):
    #TODO: Define configuration in ENV variables
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        isAuthenticated = False
        await websocket.send(client_id)
        print("Connected to the chat server!")
        
        while True:
            # Choose action: register or login
            action = input("Type 'register' to create a new account or 'login' to access an existing one: ").strip().lower()
            if action == 'register':
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
                    isAuthenticated = True
                    break
            
            # For login
            elif action == 'login':
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                # Repeated code in register and login, create a function
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                await websocket.send(f"{username},{password_hash}")
                auth_response = await websocket.recv()
                print(auth_response)

                if auth_response != "Authentication successful":
                    print('Authenticaltion Failed! Try again.')
                    isAuthenticated = False
                    continue
                isAuthenticated = True                
            
            # Select target user
            if isAuthenticated:
                # Receive server public key

                # Start sending and receiving messages concurrently
                send_task = asyncio.create_task(send_messages(websocket))
                receive_task = asyncio.create_task(receive_messages(websocket))

                # Wait for both tasks to finish (they won't, since they're infinite loops)
                await asyncio.gather(send_task, receive_task)

if __name__ == "__main__":
    client_id = str(uuid.uuid4())  # Generate a random UUID as client ID
    asyncio.run(chat_client(client_id))
