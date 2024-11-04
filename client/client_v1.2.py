import asyncio
import websockets
import uuid
import aioconsole

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
    async with websockets.connect("ws://localhost:6789") as websocket:
        await websocket.send(client_id)
        print("Connected to the chat server!")

        # Start sending and receiving messages concurrently
        send_task = asyncio.create_task(send_messages(websocket))
        receive_task = asyncio.create_task(receive_messages(websocket))

        # Wait for both tasks to finish (they won't, since they're infinite loops)
        await asyncio.gather(send_task, receive_task)

# Run the client
client_id = str(uuid.uuid4())  # Generate a random UUID as client ID
asyncio.run(chat_client(client_id))
