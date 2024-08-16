import streamlit as st
import os
import pandas as pd
import random
import pymongo

client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["NyomNyom"]
collection = db["User"]

def display_random_tab(food, image_directory):
    st.header("Find a Random Meal")
    st.subheader("🥕 🍅 🥑 🌶️ 🧅 🧄 🫚 🌽 🍗 🥩 🥚 🥒 🦐 🥦 🍋 🥓 🧀")

    # Radio button to select between search methods
    search_type = st.radio(
        "Choose how you'd like to find a meal:",
        ("Find a Random Meal Based on Ingredients", "Find a Completely Random Meal")
    )

    # Initialize a session state variable to hold the current meal
    if 'current_meal' not in st.session_state:
        st.session_state.current_meal = None

    # Show the input and button based on the radio selection
    if search_type == "Find a Random Meal Based on Ingredients":
        # Input bar for ingredients
        ingredients_input = st.text_input("Enter the ingredients you have (comma-separated):")

        if ingredients_input and st.button("Find Meal Based on Ingredients"):
            # Split the input into a list of ingredients
            ingredients = [ingredient.strip().lower() for ingredient in ingredients_input.split(',')]
            
            # Filter meals that contain any of the input ingredients
            filtered_food = food[food['Ingredients'].apply(lambda x: any(ingredient in x.lower() for ingredient in ingredients))]
            
            if not filtered_food.empty:
                # Randomly select one meal from the filtered results and store it in session state
                st.session_state.current_meal = filtered_food.sample(1).iloc[0]
            else:
                st.warning("No meals found with the given ingredients.")
                st.session_state.current_meal = None

    elif search_type == "Find a Completely Random Meal":
        if st.button("I'm Ready to Go Random"):
            # Pick a random meal from the entire dataset and store it in session state
            st.session_state.current_meal = food.sample(1).iloc[0]


    # Display the current meal
    if st.session_state.current_meal is not None:
        display_meal = st.session_state.current_meal
        image_path = os.path.join(image_directory, display_meal['Image_Name'] + '.jpg')

        st.markdown(f"## {display_meal['Title']}")
        
        if os.path.exists(image_path):
            st.image(image_path, use_column_width=True)
        else:
            st.error(f"Image not found: {display_meal['Image_Name']}")

        st.markdown(f"**Ingredients:** {display_meal['Ingredients']}")
        st.markdown(f"**Instructions:** {display_meal['Instructions']}")

        # Add to Favorites Button
        unique_key = f"add_fav_{display_meal['Index']}"
        if st.button("Add to Favorites 🩷", key=unique_key):
            if st.session_state.get('logged_in_user'):
                username = st.session_state['logged_in_user']
                # st.write(f"Adding {display_meal['Title']} to favorites for user {username}")
                add_to_favorites(username, display_meal['Title'], display_meal["Index"])
                st.success(f"{display_meal['Title']} has been added to your favorites! 😉")
            else:
                st.error("You must be logged in to add to favorites.")


def add_to_favorites(username, food_title, food_index):
    """Add a food item to the user's favorites in MongoDB with the index."""
    # Find the user by username and add the food title along with the index to the favorites list
    food_index = int(food_index)
    collection.update_one(
        {"username": username},
        {"$addToSet": {"favorites": {"title": food_title, "index": food_index}}}  # $addToSet ensures no duplicates
    )

def remove_from_favorites(username, food_title, food_index):
    """Remove a food item from the user's favorites in MongoDB."""
    food_index = int(food_index)
    collection.update_one(
        {"username": username},
        {"$pull": {"favorites": {"title": food_title, "index": food_index}}}  # $pull removes the item from the array
    )