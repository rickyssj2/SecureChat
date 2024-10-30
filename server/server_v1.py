import asyncio
import websockets

# Store connected clients
connected_clients = {}

async def echo(websocket, path):
    client_id = await websocket.recv()
    connected_clients[client_id] = websocket
    print(f"Client {client_id} connected.")

    try:
        async for message in websocket:
            print(f"Received from {client_id}: {message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {client_id} disconnected.")
    finally:
        del connected_clients[client_id]

async def main():
    server = await websockets.serve(echo, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
