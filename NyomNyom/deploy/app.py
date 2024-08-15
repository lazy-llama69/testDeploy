import streamlit as st
import pandas as pd 
from matplotlib import pyplot as plt
from plotly import graph_objs as go
from sklearn.linear_model import LinearRegression
import numpy as np 
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import urlencode
import os
import pymongo
import random 
import time 


client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["NyomNyom"]
collection = db["User"]

def main():

    tab1, tab2, tab3 = st.tabs(["Home", "Random", "Favourites"])

    with tab1:
        username = st.session_state.get('username', None)
        st.title("Welcome back " + username + " 👋🏻")

        # Load the food and ratings data only once and store them in session state
        if 'food_data' not in st.session_state:
            st.session_state.food_data = pd.read_csv("input/recipes.csv")
            st.session_state.food_data.dropna(inplace=True)

        food = st.session_state.food_data

        # Directory where images are stored
        image_directory = 'input/Food Images'

        # Initialize session state for selected food and view index
        if 'selected_food' not in st.session_state:
            st.session_state.selected_food = None

        # Define functions to switch views
        def switch_to_details(food_title):
            st.session_state.selected_food = food_title

        def switch_to_search():
            st.session_state.selected_food = None

        # Display the current view
        if st.session_state.selected_food is None:
            # Search and recommendation view
            st.subheader("What do you feel like eating today? 🍴")
            st.subheader("🍔 🍜 🍱 🌮 🥟 🍣 🥞 🧋 🍰 🥐 🥗 🍲 🍛")

            search_term = st.text_input("Search for a food item:")

            # Display results only if a search term is entered
            if search_term:
                filtered_food = food[food['Title'].str.contains(search_term, case=False, na=False)].head(18)

                if not filtered_food.empty:
                    N_cards_per_row = 3

                    for n_row, row in filtered_food.reset_index().iterrows():
                        i = n_row % N_cards_per_row
                        if i == 0:
                            st.write("---")
                            cols = st.columns(N_cards_per_row, gap="large")

                        with cols[i]:
                            # Construct the full image path with extension
                            image_path = os.path.join(image_directory, row['Image_Name'] + '.jpg')

                            if os.path.exists(image_path):
                                st.image(image_path, use_column_width=True)
                            else:
                                st.error(f"Image not found: {row['Image_Name']}")

                            st.markdown(f"**{row['Title'].strip()}**")

                            # Clickable food title
                            if st.button(row['Title'], key=row['Title']):
                                switch_to_details(row['Title'])  # Switch to the Details view
                                st.rerun()  # Force rerun to update the view

            # Display recommendations below the search bar
            st.subheader("Recommended Meals Based on Your Favorites")

            if username:
                user = collection.find_one({"username": username})
                favorite_titles = user.get("favorites", [])

                recommendations = food_recommendation_from_precomputed(food, favorite_titles, top_n=9)

                if recommendations:
                    N_cards_per_row = 3  # Number of cards per row
                    for n_row, rec_title in enumerate(recommendations):
                        recommended_food_item = food[food['Title'] == rec_title].iloc[0]
                        image_path = os.path.join(image_directory, recommended_food_item['Image_Name'] + '.jpg')

                        i = n_row % N_cards_per_row
                        if i == 0:
                            st.write("---")
                            cols = st.columns(N_cards_per_row, gap="large")

                        with cols[i]:
                            if os.path.exists(image_path):
                                st.image(image_path, use_column_width=True)
                            else:
                                st.error(f"Image not found: {recommended_food_item['Image_Name']}")

                            # Clickable food title
                            if st.button(rec_title, key=rec_title):
                                switch_to_details(rec_title)  # Switch to the Details view
                                st.rerun()  # Trigger a rerun to update the view

        else:
            # Unified Details view
            selected_food_item = food[food['Title'] == st.session_state.selected_food]
            if not selected_food_item.empty:
                food_item = selected_food_item.iloc[0]

                image_path = os.path.join(image_directory, food_item['Image_Name'] + '.jpg')

                if os.path.exists(image_path):
                    st.image(image_path, use_column_width=True)
                else:
                    st.error(f"Image not found: {image_path}")

                st.markdown(f"## {food_item['Title']}")
                st.markdown(f"**Ingredients:** {food_item['Ingredients']}")
                st.markdown(f"**Instructions:** {food_item['Instructions']}")

                # Add to Favorites Button
                if st.button("Add to Favorites 🩷"):
                    if st.session_state['logged_in_user']:
                        username = st.session_state['logged_in_user']
                        add_to_favorites(username, food_item['Title'])
                        st.success(f"{food_item['Title']} has been added to your favorites! 😉")

                if st.button("Go back"):
                    switch_to_search()  # Switch back to the Search view
                    st.rerun()  # Force rerun to update the view
            else:
                st.error("The selected food item could not be found.")
                if st.button("Go back"):
                    switch_to_search()
                    st.rerun()





    # Tab 2: Find a Meal
    with tab2:
        st.header("Find a Random Meal Based on Your Ingredients ")
        st.subheader("🥕 🍅 🥑 🌶️ 🧅 🧄 🫚 🌽 🍗 🥩 🥚 🥒 🦐 🥦 🍋 🥓 🧀")
        
        # Input bar for ingredients
        ingredients_input = st.text_input(
            "Enter the ingredients you have (comma-separated):"
        )

        # Initialize the state for random meal
        if 'random_meal' not in st.session_state:
            st.session_state.random_meal = None

        # Handle the search input
        if ingredients_input:
            # Split the input into a list of ingredients
            ingredients = [ingredient.strip().lower() for ingredient in ingredients_input.split(',')]
            
            # Filter meals that contain any of the input ingredients
            filtered_food = food[food['Ingredients'].apply(lambda x: any(ingredient in x.lower() for ingredient in ingredients))]
            
            if not filtered_food.empty:
                # Randomly select one meal from the filtered results and store it in session state
                st.session_state.random_meal = filtered_food.sample(1).iloc[0]
                st.session_state.random_meal_type = "filtered"

        # Center-align the button using columns
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("Find a Random Meal"):
                # Pick a random meal from the entire dataset and store it in session state
                st.session_state.random_meal = food.sample(1).iloc[0]
                st.session_state.random_meal_type = "random"

        # Display the random or filtered meal
        if st.session_state.random_meal is not None:
            random_meal = st.session_state.random_meal
            image_path = os.path.join(image_directory, random_meal['Image_Name'] + '.jpg')

            st.markdown(f"## {random_meal['Title']}")
            
            if os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
            else:
                st.error(f"Image not found: {random_meal['Image_Name']}")
            
            st.markdown(f"**Ingredients:** {random_meal['Ingredients']}")
            st.markdown(f"**Instructions:** {random_meal['Instructions']}")

            # Add to Favorites Button
            if st.button("Add to Favorites 🩷"):
                if st.session_state['logged_in_user']:
                    username = st.session_state['logged_in_user']
                    add_to_favorites(username, random_meal['Title'])
                    st.success(f"{random_meal['Title']} has been added to your favorites! 😉")

        # No matching meals found
        elif ingredients_input and st.session_state.random_meal_type == "filtered" and st.session_state.random_meal is None:
            st.warning("No meals found with the given ingredients.")


    with tab3:
        st.title("Your Favorite Meals 🩷 ")
        username = st.session_state.get('username', None)  # Get the logged-in username
        
        # Retrieve the user's favorite meals from MongoDB
        user = collection.find_one({"username": username}) if username else None
        favorites = user.get("favorites", []) if user else []

        if favorites:
            # Load the food data
            food = st.session_state.food_data

            # Filter the food data to only include favorite items
            favorite_foods = food[food['Title'].isin(favorites)]

            if not favorite_foods.empty:
                N_cards_per_row = 3  # Number of cards per row

                # Check if a specific food is selected to show details
                selected_favorite = st.session_state.get('selected_favorite', None)

                if selected_favorite:
                    # Show the details of the selected food
                    selected_food_item = food[food['Title'] == selected_favorite]

                    if not selected_food_item.empty:
                        food_item = selected_food_item.iloc[0]
                        image_path = os.path.join(image_directory, food_item['Image_Name'] + '.jpg')

                        if os.path.exists(image_path):
                            st.image(image_path, use_column_width=True)
                        else:
                            st.error(f"Image not found: {food_item['Image_Name']}")
                        
                        st.markdown(f"## {food_item['Title']}")
                        st.markdown(f"**Ingredients:** {food_item['Ingredients']}")
                        st.markdown(f"**Instructions:** {food_item['Instructions']}")

                        # Add a "Remove from Favorites" button
                        if st.button("Remove from Favorites 💔"):
                            remove_from_favorites(username, food_item['Title'])
                            st.success(f"{food_item['Title']} has been removed from your favorites! 🥹")
                            # Delay to allow the success message to appear
                            time.sleep(2)  # Delay for 2 seconds
                            st.session_state.selected_favorite = None  # Reset the selected favorite
                            st.rerun()  # Rerun to update the view

                        if st.button("Back to Favorites"):
                            st.session_state.selected_favorite = None  # Reset the selected favorite
                            st.rerun()  # Rerun to update the view
                else:
                    # Display the list of favorite foods
                    for n_row, row in favorite_foods.reset_index().iterrows():
                        i = n_row % N_cards_per_row
                        if i == 0:
                            st.write("---")
                            cols = st.columns(N_cards_per_row, gap="large")

                        with cols[i]:
                            # Construct the full image path with extension
                            image_path = os.path.join(image_directory, row['Image_Name'] + '.jpg')
                            
                            if os.path.exists(image_path):
                                st.image(image_path, use_column_width=True)
                            else:
                                st.error(f"Image not found: {row['Image_Name']}")

                            # Create a centered button for the title
                            st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                            
                            if st.button(row['Title'], key=row['Title']):
                                st.session_state.selected_favorite = row['Title']  # Store the selected title
                                st.rerun()  # Rerun to update the view
                            
                            st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("You don't have any favorites yet.")
        else:
            st.warning("You don't have any favorites yet.")


def switch_to_details(food_title):
    st.session_state.selected_food = food_title

def switch_to_search():
    st.session_state.selected_food = None


def add_to_favorites(username, food_title):
    """Add a food item to the user's favorites in MongoDB."""
    # Find the user by username and add the food title to the favorites list
    collection.update_one(
        {"username": username},
        {"$addToSet": {"favorites": food_title}}  # $addToSet ensures no duplicates
    )

def remove_from_favorites(username, food_title):
    """Remove a food item from the user's favorites in MongoDB."""
    collection.update_one(
        {"username": username},
        {"$pull": {"favorites": food_title}}  # $pull removes the item from the array
    )


import json
def load_precomputed_recommendations():
    with open("precomputed_recommendations.json", "r") as f:
        return json.load(f)

precomputed_recommendations = load_precomputed_recommendations()

def food_recommendation_from_precomputed(food, favorite_titles=None, top_n=9):
    all_recommendations = []

    for food_title in favorite_titles:
        if food_title in precomputed_recommendations:
            all_recommendations.extend(precomputed_recommendations[food_title])

    all_recommendations = [rec for rec in all_recommendations if rec not in favorite_titles]
    unique_recommendations = pd.Series(all_recommendations).value_counts().index.tolist()
    return unique_recommendations[:top_n]