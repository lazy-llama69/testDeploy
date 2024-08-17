import streamlit as st
import os
import pandas as pd
import random
import pymongo

client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["NyomNyom"]
collection = db["User"]

def display_random_tab(food, image_directory):
    st.title("Find a Random Meal 🎲")
    st.write("Feeling indecisive? Let us help! Whether you want to whip up something with what’s in your kitchen or leave it all to chance, we’ve got the perfect meal for you. Just enter your ingredients or let us pick something totally random. Your next meal is just a click away!")
    st.subheader("🥕 🍅 🥑 🌶️ 🧅 🧄 🫚 🌽 🍗 🥩 🥚 🥒 🦐 🥦 🍋 🥓 🧀")
    st.write("---")

    # Radio button to select between search methods
    search_type = st.radio(
        "Choose how you'd like to find a meal:",
        ("Find a Random Meal Based on Ingredients", "Find a Completely Random Meal")
    )

    # Initialize a session state variable to hold the current meal
    if 'current_meal' not in st.session_state:
        st.session_state.current_meal = None

    # Reset the current meal when the search type changes
    if 'search_type' not in st.session_state or st.session_state.search_type != search_type:
        st.session_state.current_meal = None
        st.session_state.search_type = search_type

        
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

        # st.markdown(f"**Ingredients:** {display_meal['Ingredients']}")
        # st.markdown(f"**Instructions:** {display_meal['Instructions']}")

        # Format ingredients and remove brackets
        formatted_ingredients = format_ingredients(display_meal['Ingredients'])
        st.markdown("<h3 style='font-size:24px;'>Ingredients:</h3>", unsafe_allow_html=True)
        st.markdown(f"{formatted_ingredients}")
        
        # Format instructions
        formatted_instructions = format_instructions(display_meal['Instructions'])
        st.markdown("<h3 style='font-size:24px;'>Instructions:</h3>", unsafe_allow_html=True)
        st.markdown(f"{formatted_instructions}")

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


def format_ingredients(ingredients):
    # Check if the ingredients are in string format with brackets
    if isinstance(ingredients, str):
        # Remove the square brackets and split the string into individual ingredients
        ingredients = ingredients.strip("[]")  # Strip square brackets
        ingredients = ingredients.split(", ")  # Split by comma and space
        
        # Further cleaning to remove quotes if necessary
        ingredients = [ingredient.strip().strip("'").strip('"') for ingredient in ingredients]
    
    # Convert the list of ingredients to a formatted string with each ingredient on a new line
    formatted_ingredients = "\n".join([f"- {ingredient.strip()}" for ingredient in ingredients])
    
    return formatted_ingredients


def format_instructions(instructions):
    # Split instructions based on a period followed by a space.
    # This assumes each instruction ends with a period and a space.
    instructions_list = instructions.split(". ")
    # Re-add the period and create a numbered list of instructions.
    formatted_instructions = "\n".join([f"{i+1}. {instruction.strip()}." for i, instruction in enumerate(instructions_list) if instruction])
    return formatted_instructions

