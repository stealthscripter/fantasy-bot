import json
import os

REGISTERED_USERS_FILE = "registered_users.json"

def load_users():
    if os.path.exists(REGISTERED_USERS_FILE):
        with open(REGISTERED_USERS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_users(users):
    with open(REGISTERED_USERS_FILE, "w") as file:
        json.dump(users, file)
