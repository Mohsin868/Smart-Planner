import streamlit as st

st.write("URL:", st.secrets["SUPABASE_URL"])

key = st.secrets["SUPABASE_KEY"]

st.write("Key Length:", len(key))
st.write("Full Key:", key)