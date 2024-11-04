import asyncio
import websockets
import uuid
import threading

async def send_messages(websocket):
    while True:
        message = await message_queue.get()  # Wait for messages from the queue
        print(f"Sending message: {message}")  # Debug print
        await websocket.send(message)

async def receive_messages(websocket):
    while True:
        response = await websocket.recv()
        print(f"Other: {response}")

def input_thread():
    # Create a new event loop for this thread
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    
    while True:
        message = input("You: ")
        asyncio.run_coroutine_threadsafe(message_queue.put(message), new_loop)

async def chat_client(client_id):
    async with websockets.connect("ws://localhost:6789") as websocket:
        await websocket.send(client_id)
        print("Connected to the chat server!")

        # Start the input thread
        threading.Thread(target=input_thread, daemon=True).start()

        # Start sending and receiving messages concurrently
        send_task = asyncio.create_task(send_messages(websocket))
        receive_task = asyncio.create_task(receive_messages(websocket))

        # Wait for both tasks to finish (they won't, since they're infinite loops)
        await asyncio.gather(send_task, receive_task)

# Create a queue for message passing
message_queue = asyncio.Queue()

# Run the client
client_id = str(uuid.uuid4())  # Generate a random UUID as client ID
asyncio.run(chat_client(client_id))
