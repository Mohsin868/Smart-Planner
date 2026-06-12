import streamlit as st
from supabase import create_client

def get_supabase():
    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")

    if not url or not key:
        st.error("Missing Supabase credentials")
        st.stop()

    return create_client(url, key)