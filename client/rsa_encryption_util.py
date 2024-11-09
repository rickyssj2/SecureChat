# rsa_encryption_util.py
import rsa

class RSAEncryptionUtil:
    def __init__(self):
        # Generate RSA public and private keys
        self.public_key, self.private_key = rsa.newkeys(2048)

    def encrypt(self, message: str, public_key) -> bytes:
        # Encrypt message with the recipient's public key
        return rsa.encrypt(message.encode(), public_key)

    def decrypt(self, encrypted_message: bytes) -> str:
        # Decrypt message with the client's private key
        return rsa.decrypt(encrypted_message, self.private_key).decode()

    def get_public_key_bytes(self) -> bytes:
        # Export public key in PEM format for easy transfer
        return self.public_key.save_pkcs1()

    @staticmethod
    def load_public_key(public_key_bytes: bytes):
        # Load public key from PEM format
        return rsa.PublicKey.load_pkcs1(public_key_bytes)
