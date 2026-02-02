import hashlib
import streamlit as st
from db import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        user_id = cur.lastrowid

        # Create stats row
        cur.execute(
            "INSERT INTO stats (user_id) VALUES (?)",
            (user_id,)
        )

        conn.commit()
        return True, "Registration successful!"
    except:
        return False, "Username already exists!"
    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, password FROM users WHERE username = ?",
        (username,)
    )
    user = cur.fetchone()
    conn.close()

    if not user:
        return False, "User not found"

    user_id, stored_password = user

    if stored_password != hash_password(password):
        return False, "Incorrect password"

    st.session_state.user = username
    st.session_state.user_id = user_id
    st.session_state.logged_in = True

    return True, "Login successful"
