import streamlit as st
import pymongo
# Replace with your actual MongoDB connection string
client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["NyomNyom"]
collection = db["User"]

def register(username, password):
    """Register a new user by adding their credentials to MongoDB."""
    # Check if the username already exists in the database
    if collection.find_one({"username": username}):
        return False  # User already exists
    
    # If the username is unique, insert the new user into the collection
    user_data = {
        "username": username,
        "password": password,  # Note: In a real application, passwords should be hashed
        "meals_eaten": [],  # Initialize with an empty list
        "favorites": []     #Intialize a favorites empty list
    }
    collection.insert_one(user_data)
    return True

def main():
    st.title("Welcome to Nyom Nyom! 🤤 ")
    st.write("Your ultimate meal discovery app! Whether you're indecisive or know exactly what you want, we've got you covered. Save your favorite recipes for quick access anytime, explore new cuisines, and get personalized recommendations based on your tastes. Feeling adventurous? Let our random meal generator surprise you with delicious choices! Plus, there's a hidden special feature waiting to be discovered—log in and start your culinary journey today! 🧑🏼‍🍳")
    st.write("---")
    st.header("Sign Up")

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
