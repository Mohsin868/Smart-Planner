import hashlib
from db import get_supabase

supabase = get_supabase()


# ---------------- HASH PASSWORD ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------- REGISTER USER ----------------
def register_user(username, password):

    hashed = hash_password(password)

    # check if user exists
    existing = supabase.table("users") \
        .select("*") \
        .eq("username", username) \
        .execute()

    if existing.data:
        return False, "Username already exists"

    supabase.table("users").insert({
        "username": username,
        "password": hashed
    }).execute()

    return True, "User registered successfully"


# ---------------- LOGIN USER ----------------
def login_user(username, password):

    hashed = hash_password(password)

    response = supabase.table("users") \
        .select("*") \
        .eq("username", username) \
        .eq("password", hashed) \
        .execute()

    if response.data:
        user = response.data[0]
        return True, user["id"]

    return False, "Invalid username or password"