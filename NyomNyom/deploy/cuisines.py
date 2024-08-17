import streamlit as st
import os
import pandas as pd
import time 
# from streamlit_extras.let_it_rain import rain

cuisines = {
    "Korean 🇰🇷": ["korean", "kimchi", "bulgogi", "bibimbap", "tteokbokki", "kimbap", "gimbap", "galbi", "japchae", "soondubu", "mandu"],
    "Italian 🇮🇹": ["italian", "pasta", "pizza", "lasagna", "risotto", "gelato", "gnocchi", "bruschetta", "tiramisu", "carbonara", "spaghetti"],
    "Mexican 🇲🇽": ["mexican", "taco", "burrito", "quesadilla", "enchilada", "guacamole", "tamale", "salsa", "churro", "mole"],
    "Japanese 🇯🇵": ["japanese", "sushi", "ramen", "tempura", "sashimi", "udon", "miso", "teriyaki", "gyoza", "matcha"],
    "Indian 🇮🇳": ["indian", "curry", "biryani", "tandoori", "samosa", "dal", "naan", "rogan josh", "paneer", "masala"],
    "Chinese 🇨🇳": ["chinese", "dumpling", "noodle", "sweet and sour", "kung pao", "fried rice", "spring roll", "dim sum", "baozi", "mapo tofu"],
    "Thai 🇹🇭": ["thai", "pad thai", "green curry", "tom yum", "som tam", "satay", "massaman", "mango sticky rice", "larb", "red curry"],
    "Vietnamese 🇻🇳": ["vietnamese", "pho", "banh mi", "spring roll", "bun cha", "banh xeo", "ca kho to", "goi cuon", "banh cuon", "nuoc cham"],
}


def display_cuisine_tab(collection, image_directory, food):
    st.title("Explore Food by Cuisine 🌏")
    st.write("Choose a cuisine and discover authentic recipes that bring global flavors to your table. Ready to find your next favorite dish? Let's get cooking!")
    if 'selected_food' not in st.session_state:
        st.session_state.selected_food = None

    # # Ensure 'Index' column is numeric
    # food['Index'] = pd.to_numeric(food['Index'], errors='coerce')

    selected_cuisine = st.selectbox("Choose a cuisine", list(cuisines.keys()))

    if selected_cuisine:
        keywords = cuisines[selected_cuisine]
        filtered_food = food[food['Title'].str.contains('|'.join(keywords), case=False, na=False)]

    
    # Unified Details view for the selected food item
        if st.session_state.selected_food is None:
            display_food_cards(filtered_food, image_directory)

        else: 
            selected_food_item = food[(food['Index'] == st.session_state.selected_food['index']) &
                                (food['Title'] == st.session_state.selected_food['title'])]
            # print("selected_food_item" + str(selected_food_item))
            if not selected_food_item.empty:
                food_item = selected_food_item.iloc[0]

                image_path = os.path.join(image_directory, food_item['Image_Name'] + '.jpg')

                if os.path.exists(image_path):
                    st.image(image_path, use_column_width=True)
                else:
                    st.error(f"Image not found: {image_path}")

                st.markdown(f"## {food_item['Title']}")
                # st.markdown(f"**Ingredients:** {food_item['Ingredients']}")
                # st.markdown(f"**Instructions:** {food_item['Instructions']}")
                
                # Format ingredients and remove brackets
                formatted_ingredients = format_ingredients(food_item['Ingredients'])
                st.markdown("<h3 style='font-size:24px;'>Ingredients:</h3>", unsafe_allow_html=True)
                st.markdown(f"{formatted_ingredients}")
                
                # Format instructions
                formatted_instructions = format_instructions(food_item['Instructions'])
                st.markdown("<h3 style='font-size:24px;'>Instructions:</h3>", unsafe_allow_html=True)
                st.markdown(f"{formatted_instructions}")

                # Add to Favorites Button
                # if st.button("Add to Favorites 🩷"):
                if st.button("Add to Favorites 🩷", key=f"fav_{food_item['Title']}_{food_item['Index']}"):
                    if st.session_state['logged_in_user']:
                        username = st.session_state['logged_in_user']
                        add_to_favorites(collection, username, food_item['Title'], food_item["Index"])
                        st.success(f"{food_item['Title']} has been added to your favorites! 😉")
                        time.sleep(2)
                        st.rerun()

                # if st.button("Go back"):
                if st.button("Go back", key=f"go_back_{st.session_state.selected_food['index']}"):
                    st.session_state.selected_food = None
                    st.rerun()  # Force rerun to go back to the previous view
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
            unique_key = f"{row['Title']}_{row['Index']}_{n_row}"
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


