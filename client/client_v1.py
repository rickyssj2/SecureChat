import asyncio
import websockets

async def hello(id):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(id)
        while True:
            message = input(f"Send a message from {id}: ")
            await websocket.send(message)

if __name__ == "__main__":
    client_id = input("Enter your client ID: ")
    asyncio.run(hello(client_id))
