import streamlit as st

# Example credentials (in-memory for simplicity)
CREDENTIALS = {
    "user1": "password1",
    "user2": "password2"
}

def authenticate(username, password):
    """Check if the provided username and password match any in the credentials."""
    if username in CREDENTIALS and CREDENTIALS[username] == password:
        return True
    return False

def main():
    st.title("Log In")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Display login form
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

    else:
        st.write(f"Welcome {st.session_state.username}!")
        st.write("You are now logged in.")

if __name__ == "__main__":
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if st.session_state.page == "login":
        main()
    elif st.session_state.page == "sign_in":
        import sign_in
        sign_in.main()
