import streamlit as st
from auth import login_user, register_user
from dashboard import launch_dashboard

# Initialize session_state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# ---------- LOGGED IN ----------
if st.session_state["logged_in"]:
    st.sidebar.success(f"Logged in as: {st.session_state['user']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    launch_dashboard()

# ---------- LOGIN / REGISTER ----------
else:
    st.title("🧠 Smart Life Planner")
    st.subheader("Login or Register to continue")

    choice = st.radio("Select option:", ["Login", "Register"])

    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.button("Login")

        if login_btn:
            success, msg = login_user(username, password)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    elif choice == "Register":
        username = st.text_input("Choose a Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_btn = st.button("Register")

        if register_btn:
            if password != confirm_password:
                st.error("Passwords do not match!")
            else:
                success, msg = register_user(username, password)
                if success:
                    st.success(msg)
                    st.info("Go to Login tab to access your account.")
                else:
                    st.error(msg)
