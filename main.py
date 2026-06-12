import streamlit as st
from auth import login_user, register_user
from dashboard import launch_dashboard

# ---------------- SESSION STATE INIT ----------------
defaults = {
    "logged_in": False,
    "user": None,
    "user_id": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- LOGGED IN VIEW ----------------
if st.session_state.logged_in:

    st.sidebar.success(f"👤 Logged in as: {st.session_state.user}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    launch_dashboard()


# ---------------- AUTH VIEW ----------------
else:
    st.title("🧠 Smart Life Planner")
    st.subheader("Login or Register to continue")

    choice = st.radio("Select option:", ["Login", "Register"])

    # ---------- LOGIN ----------
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, result = login_user(username, password)

            if success:
                st.session_state.logged_in = True
                st.session_state.user_id = result
                st.session_state.user = username

                st.success("Login successful!")
                st.rerun()
            else:
                st.error(result)

    # ---------- REGISTER ----------
    else:
        username = st.text_input("Choose a Username")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if password != confirm:
                st.error("Passwords do not match!")
            else:
                success, msg = register_user(username, password)

                if success:
                    st.success(msg)
                    st.info("You can now login.")
                else:
                    st.error(msg)