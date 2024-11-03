import asyncio
import websockets

async def chat_client():
    async with websockets.connect("ws://localhost:6789") as websocket:
        print("Connected to the chat server!")
        while True:
            message = input("You: ")
            await websocket.send(message)
            response = await websocket.recv()
            print(f"Other: {response}")

# Run the client
asyncio.run(chat_client())
