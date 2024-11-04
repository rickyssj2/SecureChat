import asyncio
import websockets
import uuid

async def chat_client(client_id):
    async with websockets.connect("ws://localhost:6789") as websocket:
        await websocket.send(client_id)
        print("Connected to the chat server!")
        while True:
            message = input("You: ")
            await websocket.send(message)
            response = await websocket.recv()
            print(f"Other: {response}")

# Run the client
client_id = str(uuid.uuid4())  # Generate a random UUID as client ID
asyncio.run(chat_client(client_id))
