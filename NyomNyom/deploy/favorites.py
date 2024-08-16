import streamlit as st
import os
import pandas as pd
import time


def display_favourites_tab(collection, image_directory, food):
    st.title("Your Favorite Meals 🩷 ")
    username = st.session_state.get('username', None)  # Get the logged-in username
    
    # Retrieve the user's favorite meals from MongoDB
    user = collection.find_one({"username": username}) if username else None
    favorites = user.get("favorites", []) if user else []

    if favorites:
        favorite_foods = pd.DataFrame([
            food_item.iloc[0] for favorite in favorites
            if not (food_item := food[(food['Index'] == favorite['index']) & (food['Title'] == favorite['title'])]).empty
        ])

        if not favorite_foods.empty:
            N_cards_per_row = 3  # Number of cards per row

            # Check if a specific food is selected to show details
            selected_favorite = st.session_state.get('selected_favorite', None)

            if selected_favorite:
                # Show the details of the selected food
                selected_food_item = food[(food['Index'] == selected_favorite['index']) & (food['Title'] == selected_favorite['title'])]

                if selected_food_item.empty:
                    st.warning(f"The selected food item '{selected_favorite['title']}' could not be found.")
                else:
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
                        remove_from_favorites(collection, username, food_item['Title'], food_item['Index'])
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
                        
                        if st.button(row['Title'], key=row['Index']):
                            st.session_state.selected_favorite = {'title': row['Title'], 'index': row['Index']}  # Store the selected title and index
                            st.rerun()  # Rerun to update the view
                        
                        st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("You don't have any favorites yet.")
    else:
        st.warning("You don't have any favorites yet.")


def remove_from_favorites(collection, username, food_title, food_index):
    """Remove a food item from the user's favorites in MongoDB."""
    food_index = int(food_index)
    collection.update_one(
        {"username": username},
        {"$pull": {"favorites": {"title": food_title, "index": food_index}}}  # $pull removes the item from the array
    )