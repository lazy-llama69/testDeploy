import streamlit as st
import pandas as pd 
import os

# Example credentials (in-memory for simplicity)
CREDENTIALS = {
    "u": "u",
    "user2": "password2"
}

def authenticate(username, password):
    """Check if the provided username and password match any in the credentials."""
    return CREDENTIALS.get(username) == password

def login_page():
    st.title("Log In")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Log in")

    if login_button:
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  # Refresh the page to load the main app
        else:
            st.error("Invalid username or password")

    if st.button("Go to Sign In page"):
        st.session_state.page = "sign_in"
        st.rerun()

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.logged_in:
        import app
        app.main()
    else:
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "sign_in":
            import sign_in
            sign_in.main()

if __name__ == "__main__":
    main()
