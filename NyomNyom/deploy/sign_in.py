import streamlit as st
from login import CREDENTIALS

def register(username, password):
    """Register a new user by adding their credentials to the store."""
    if username in CREDENTIALS:
        return False  # User already exists
    CREDENTIALS[username] = password
    return True

def display():
    st.title("Sign In")

    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    sign_in_button = st.button("Sign in")

    if sign_in_button:
        if register(new_username, new_password):
            st.success("Registration successful! Redirecting to Log In page...")
            st.session_state.page = "login"
            st.experimental_rerun()  # Redirect to login page
        else:
            st.error("Username already exists. Please choose another.")
