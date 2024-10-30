import asyncio
import websockets
import rsa
import base64

# Generate RSA keys
(server_public_key, server_private_key) = rsa.newkeys(512)

async def chat_server(websocket, path):
    # Step 1: Receive the client's public key
    client_public_key_data = await websocket.recv()
    client_public_key = rsa.PublicKey.load_pkcs1(base64.b64decode(client_public_key_data))

    # Step 2: Send the server's public key to the client
    server_public_key_data = server_public_key.save_pkcs1(format='PEM')
    await websocket.send(base64.b64encode(server_public_key_data).decode())

    while True:
        encrypted_message = await websocket.recv()
        decrypted_message = rsa.decrypt(encrypted_message, server_private_key).decode('utf-8')
        print(f"Received: {decrypted_message}")
        response = f"Echo: {decrypted_message}"
        encrypted_response = rsa.encrypt(response.encode('utf-8'), client_public_key)
        await websocket.send(encrypted_response)

start_server = websockets.serve(chat_server, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
