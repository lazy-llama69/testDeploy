import streamlit as st

# Example credentials (in-memory for simplicity)
CREDENTIALS = {
    "user1": "password1",
    "user2": "password2"
}

def authenticate(username, password):
    """Check if the provided username and password match any in the credentials."""
    return CREDENTIALS.get(username) == password

def display():
    st.title("Log In")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Log in")

    if login_button:
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.experimental_rerun()  # Refresh the page after login
        else:
            st.error("Invalid username or password")

    if st.button("Go to Sign In page"):
        st.session_state.page = "sign_in"
        st.experimental_rerun()
