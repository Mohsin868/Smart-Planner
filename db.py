import psycopg2
import streamlit as st


def get_connection():
    return psycopg2.connect(
        host=st.secrets["YOUR_HOST"],
        port=st.secrets["5432"],
        dbname=st.secrets["Mohsin868's Project"],
        user=st.secrets["Mohsin868's Org"],
        password=st.secrets["00WDDkB9Ad2x6fgx"],
    )


def init_db():
    # Tables already created in Supabase
    # This function exists only to keep app structure intact
    pass
