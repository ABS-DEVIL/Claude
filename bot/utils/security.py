import secrets
import hashlib

def generate_token():
    return secrets.token_urlsafe(32)

def generate_key():
    return secrets.token_hex(16)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed
