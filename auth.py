import os
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
AUTH_FILE = "auth_users.enc"

if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY is not set")

fernet = Fernet(ENCRYPTION_KEY.encode())
_authorized_users = set()

def load_auth_users():
    global _authorized_users
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "rb") as f:
            data = f.read().strip()
            if data:
                try:
                    decrypted = fernet.decrypt(data).decode()
                    _authorized_users = set(json.loads(decrypted))
                except Exception:
                    _authorized_users = set()
    return list(_authorized_users)

def save_auth_users():
    data = json.dumps(list(_authorized_users)).encode()
    with open(AUTH_FILE, "wb") as f:
        f.write(fernet.encrypt(data))

def authorize_user(user_id):
    _authorized_users.add(int(user_id))
    save_auth_users()

def revoke_user(user_id):
    _authorized_users.discard(int(user_id))
    save_auth_users()

def is_authorized(user_id):
    return int(user_id) in _authorized_users

def get_authorized_user_ids():
    return list(_authorized_users)
