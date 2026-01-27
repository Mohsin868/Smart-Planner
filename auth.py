import streamlit as st
import json
import hashlib
import os

USERS_FILE = "data/users.json"

# Ensure data folder and users file exist
if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# ---------- HASH FUNCTION ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------- REGISTER FUNCTION ----------
def register_user(username, password):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if username in users:
        return False, "Username already exists!"
    
    users[username] = hash_password(password)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

    # Create empty files for the user
    open(f"data/{username}_tasks.csv", "a").close()
    open(f"data/{username}_routine.json", "a").close()

    return True, "Registration successful! Please login."


# ---------- LOGIN FUNCTION ----------
def login_user(username, password):
    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if username not in users:
        return False, "Username does not exist!"

    if users[username] != hash_password(password):
        return False, "Incorrect password!"

    # Set session state
    st.session_state["user"] = username
    st.session_state["logged_in"] = True
    return True, "Login successful!"
