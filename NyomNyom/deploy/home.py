import streamlit as st
import os
import pandas as pd


def display_home_tab(collection, image_directory, food):
    username = st.session_state.get('username', None)
    st.title("Welcome back " + username + " 👋🏻")

    # Initialize session state for selected food and view index
    if 'selected_food' not in st.session_state:
        st.session_state.selected_food = None

    def switch_to_details(food_title, food_index):
        st.session_state.selected_food = {'title': food_title, 'index': food_index}

    def switch_to_search():
        st.session_state.selected_food = None

    # Display the current view
    if st.session_state.selected_food is None:
        # Search and recommendation view
        st.subheader("What do you feel like eating today? 🍴")
        st.subheader("🍔 🍜 🍱 🌮 🥟 🍣 🥞 🧋 🍰 🥐 🥗 🍲 🍛")

        # Add a radio button group for choosing search criteria
        search_by = st.radio(
            "Search by:",
            ("Title", "Ingredients")
        )

        search_term = st.text_input("Search for a food item or ingredient:")

        # Display results only if a search term is entered
        if search_term:
            if search_by == "Title":
                # Search by Title
                filtered_food = food[food['Title'].str.contains(search_term, case=False, na=False)].head(18)
            elif search_by == "Ingredients":
                # Search by Ingredients
                filtered_food = food[food['Ingredients'].str.contains(search_term, case=False, na=False)].head(18)

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
                        if st.button(row['Title'], key=row['Index']):
                            switch_to_details(row['Title'], row['Index'])  # Pass title and index
                            st.rerun()  # Force rerun to update the view

        # Display recommendations below the search bar
        st.subheader("Recommended Meals Based on Your Favorites")

        if username:
            user = collection.find_one({"username": username})
            favorite_titles = user.get("favorites", [])

            recommendations = food_recommendation_from_precomputed(food, favorite_titles, top_n=9)

            if recommendations:
                N_cards_per_row = 3  # Number of cards per row
                for n_row, rec_item in enumerate(recommendations):
                    # Filter by both title and index
                    recommended_food_item = food[(food['Title'] == rec_item['title']) & (food['Index'] == rec_item['index'])]

                    if recommended_food_item.empty:
                        st.warning(f"No food item found with the title '{rec_item}'")
                        continue  # Skip to the next recommendation if no match is found
                    else:
                        recommended_food_item = recommended_food_item.iloc[0]
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

                            # Clickable food title with a unique key
                            unique_key = f"{rec_item['title']}_{rec_item['index']}"
                            if st.button(rec_item['title'], key=unique_key):
                                switch_to_details(rec_item['title'], recommended_food_item['Index'])  # Pass title and index
                                st.rerun()  # Trigger a rerun to update the view
    else:
        # Unified Details view
        selected_food_item = food[(food['Index'] == st.session_state.selected_food['index']) & 
                                (food['Title'] == st.session_state.selected_food['title'])]
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
                    add_to_favorites(collection, username, food_item['Title'], food_item["Index"])
                    st.success(f"{food_item['Title']} has been added to your favorites! 😉")

            if st.button("Go back"):
                switch_to_search()  # Switch back to the Search view
                st.rerun()  # Force rerun to update the view
        else:
            st.error("The selected food item could not be found.")
            if st.button("Go back"):
                switch_to_search()
                st.rerun()
import json
def load_precomputed_recommendations():
    with open("precomputed_recommendations.json", "r") as f:
        return json.load(f)

precomputed_recommendations = load_precomputed_recommendations()

def food_recommendation_from_precomputed(food, favorite_items=None, top_n=9):
    if favorite_items is None:
        favorite_items = []

    all_recommendations = []

    for favorite in favorite_items:
        food_index = favorite['index']  # Extract the index from the favorite dictionary
        all_recommendations.extend(precomputed_recommendations[str(food_index)])
    # print("\n\nfav items"+str(favorite_items))
    # print(precomputed_recommendations["1"])
    # all_recommendations.extend(precomputed_recommendations["1"])
    # print(all)
    # Convert the list of dictionaries to a set of tuples (title, index) for easier comparison
    favorite_set = set((fav['title'], fav['index']) for fav in favorite_items)

    # Filter out any recommendations that are already in the user's favorites
    filtered_recommendations = [
        rec for rec in all_recommendations 
        if (rec['title'], rec['index']) not in favorite_set
    ]
    
    # Sort and return the unique recommendations
    unique_recommendations = pd.Series(filtered_recommendations).value_counts().index.tolist()
    return unique_recommendations[:top_n]


def add_to_favorites(collection, username, food_title, food_index):
    """Add a food item to the user's favorites in MongoDB with the index."""
    # Find the user by username and add the food title along with the index to the favorites list
    food_index = int(food_index)
    collection.update_one(
        {"username": username},
        {"$addToSet": {"favorites": {"title": food_title, "index": food_index}}}  # $addToSet ensures no duplicates
    )

