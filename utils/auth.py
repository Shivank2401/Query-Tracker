import streamlit as st
from utils.azure_storage import load_user_data

def login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_user_data()
        user = users.get(username)
        if user and user["password"] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

def logout():
    for key in ["authenticated", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def is_authenticated():
    return st.session_state.get("authenticated", False)
