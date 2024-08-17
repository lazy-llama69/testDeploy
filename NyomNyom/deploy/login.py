import streamlit as st
import pandas as pd 
import os
import pymongo

# Example credentials (in-memory for simplicity)
client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["NyomNyom"]
collection = db["User"]


def authenticate(username, password):
    """Check if the provided username and password match any in the MongoDB collection."""
    user = collection.find_one({"username": username, "password": password})
    if user:
        st.session_state['logged_in_user'] = username
        return True
    return False

def login_page():
    st.title("Welcome to Nyom Nyom! 🤤 ")
    st.write("Your ultimate meal discovery app! Whether you're indecisive or know exactly what you want, we've got you covered. Save your favorite recipes for quick access anytime, explore new cuisines, and get personalized recommendations based on your tastes. Feeling adventurous? Let our random meal generator surprise you with delicious choices! Plus, there's a hidden special feature waiting to be discovered—log in and start your culinary journey today! 🧑🏼‍🍳")
    st.write("---")
    st.header("Log In")   

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

    # st.write("---")
    st.write("Don't have an account? Sign up now!")
    if st.button("Sign Up"):
        st.session_state.page = "sign_in"
        st.rerun()

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.logged_in:
        import main
        main.main()
    else:
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "sign_in":
            import sign_in
            sign_in.main()

if __name__ == "__main__":
    main()

