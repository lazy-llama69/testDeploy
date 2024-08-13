import streamlit as st
import pymongo
# Example credentials (in-memory for simplicity)
CREDENTIALS = {
    "user1": "password1",
    "user2": "password2"
}

# Replace with your actual MongoDB connection string
client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["NyomNyom"]
collection = db["User"]

def register(username, password):
    """Register a new user by adding their credentials to the store."""
    if username in CREDENTIALS:
        return False  # User already exists
    CREDENTIALS[username] = password
    return True

def main():
    st.title("Sign Up")

    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    sign_in_button = st.button("Register")

    if sign_in_button:
        if register(new_username, new_password):
            st.success("Registration successful! Please log in.")
            st.session_state.page = "login"  # Set the page to 'login'
            st.rerun()  # Trigger a rerun to switch pages
        else:
            st.error("Username already exists. Please choose another.")

if __name__ == "__main__":
    # Initialize session state if it doesn't exist
    if "page" not in st.session_state:
        st.session_state.page = "sign_in"
    
    # Determine which page to show
    if st.session_state.page == "sign_in":
        main()
    elif st.session_state.page == "login":
        import login
        login.main()

client.close()