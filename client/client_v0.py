import asyncio
import websockets
import rsa
import base64

# Generate RSA keys
(client_public_key, client_private_key) = rsa.newkeys(512)

async def chat_client():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        # Step 1: Send the client's public key to the server
        client_public_key_data = client_public_key.save_pkcs1(format='PEM')
        await websocket.send(base64.b64encode(client_public_key_data).decode())

        # Step 2: Receive the server's public key
        server_public_key_data = await websocket.recv()
        server_public_key = rsa.PublicKey.load_pkcs1(base64.b64decode(server_public_key_data))

        while True:
            message = input("Type your message: ")
            encrypted_message = rsa.encrypt(message.encode('utf-8'), server_public_key)
            await websocket.send(encrypted_message)
            encrypted_response = await websocket.recv()
            response = rsa.decrypt(encrypted_response, client_private_key).decode('utf-8')
            print(f"Server: {response}")

asyncio.get_event_loop().run_until_complete(chat_client())
