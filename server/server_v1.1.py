import asyncio
import websockets

# Set to hold connected clients
clients = set()

async def chat_handler(websocket, path):
    # Register the new client
    clients.add(websocket)
    try:
        async for message in websocket:
            # Broadcast the received message to all connected clients
            for client in clients:
                if client != websocket:  # Don't send the message back to the sender
                    await client.send(message)
    finally:
        # Unregister the client when done
        clients.remove(websocket)

# Start the WebSocket server
start_server = websockets.serve(chat_handler, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
print("Chat server started on ws://localhost:6789")
asyncio.get_event_loop().run_forever()
