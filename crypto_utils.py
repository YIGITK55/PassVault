from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_password(password: str) -> bytes:
    key = load_key()
    f = Fernet(key)
    return f.encrypt(password.encode())

def decrypt_password(token: bytes) -> str:
    key = load_key()
    f = Fernet(key)
    return f.decrypt(token).decode()
