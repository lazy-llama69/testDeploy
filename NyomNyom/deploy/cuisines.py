import streamlit as st
import os
import pandas as pd
import hashlib

# Define your cuisine keywords
cuisines = {
    "Korean": ["kimchi", "bulgogi", "bibimbap", "tteokbokki", "kimbap"],
    "Italian": ["pasta", "pizza", "lasagna", "risotto", "gelato"],
    "Mexican": ["taco", "burrito", "quesadilla", "enchilada", "guacamole"],
    "Japanese": ["sushi", "ramen", "tempura", "sashimi", "udon"],
    "Indian": ["curry", "biryani", "tandoori", "samosa", "dal"],
    # Add more cuisines and their associated keywords here
}

def display_cuisine_tab(collection, image_directory, food):
    st.title("Explore Food by Cuisine 🌏")

    # # Ensure 'Index' column is numeric
    # food['Index'] = pd.to_numeric(food['Index'], errors='coerce')

    selected_cuisine = st.selectbox("Choose a cuisine", list(cuisines.keys()))

    if selected_cuisine:
        keywords = cuisines[selected_cuisine]
        filtered_food = food[food['Title'].str.contains('|'.join(keywords), case=False, na=False)]

        if not filtered_food.empty:
            display_food_cards(filtered_food, image_directory)
        else:
            st.warning(f"No food items found for {selected_cuisine} cuisine.")
    
    # Unified Details view for the selected food item
    if st.session_state.selected_food is None:
        display_food_cards(collection, image_directory, food)

    else: 
        selected_food_item = food[(food['Index'] == st.session_state.selected_food['index']) &
                              (food['Title'] == st.session_state.selected_food['title'])]
        print("selected_food_item" + selected_food_item)
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
                st.session_state.selected_food = None
                st.experimental_rerun()  # Force rerun to go back to the previous view
        else:
            st.error("The selected food item could not be found.")


def display_food_cards(food_items, image_directory):
    N_cards_per_row = 3  # Number of cards per row

    for n_row, row in food_items.reset_index().iterrows():
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
            unique_key = f"{row['Title']}_{row['Index']}"
            if st.button(row['Title'], key=unique_key):
                switch_to_details(row['Title'], row['Index'])  # Pass title and index
                st.rerun()  # Force rerun to update the view



def add_to_favorites(collection, username, food_title, food_index):
    """Add a food item to the user's favorites in MongoDB with the index."""
    # Find the user by username and add the food title along with the index to the favorites list
    food_index = int(food_index)
    collection.update_one(
        {"username": username},
        {"$addToSet": {"favorites": {"title": food_title, "index": food_index}}}  # $addToSet ensures no duplicates
    )



def switch_to_details(food_title, food_index):
    st.session_state.selected_food = {'title': food_title, 'index': food_index}
    print("changed state")


# def display_food_details(collection, image_directory, food):
    # selected_food_item = food[(food['Index'] == st.session_state.selected_food['index']) &
    #                           (food['Title'] == st.session_state.selected_food['title'])]

    # if not selected_food_item.empty:
    #     food_item = selected_food_item.iloc[0]

    #     image_path = os.path.join(image_directory, food_item['Image_Name'] + '.jpg')

    #     if os.path.exists(image_path):
    #         st.image(image_path, use_column_width=True)
    #     else:
    #         st.error(f"Image not found: {image_path}")

    #     st.markdown(f"## {food_item['Title']}")
    #     st.markdown(f"**Ingredients:** {food_item['Ingredients']}")
    #     st.markdown(f"**Instructions:** {food_item['Instructions']}")

    #     # Add to Favorites Button
    #     if st.button("Add to Favorites 🩷"):
    #         if st.session_state['logged_in_user']:
    #             username = st.session_state['logged_in_user']
    #             add_to_favorites(collection, username, food_item['Title'], food_item["Index"])
    #             st.success(f"{food_item['Title']} has been added to your favorites! 😉")

    #     if st.button("Go back"):
    #         st.session_state.selected_food = None
    #         st.experimental_rerun()  # Force rerun to go back to the previous view
    # else:
    #     st.error("The selected food item could not be found.")



