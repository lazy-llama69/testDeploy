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

        # List of common allergens
        allergens = ["Gluten", "Peanuts", "Tree Nuts", "Dairy", "Soy", "Eggs", "Fish", "Shellfish"]

        # Multiselect for allergens
        selected_allergens = st.multiselect("Select Allergens to Avoid", allergens)

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

            print(f"selected_allergens before recommending: {selected_allergens}")
            recommendations = food_recommendation_from_precomputed(food, favorite_titles, 9, selected_allergens)
            # print(recommendations)
            if recommendations:
                N_cards_per_row = 3  # Number of cards per row
                for n_row, rec_item in enumerate(recommendations):
                    # Filter by both title and index
                    recommended_food_item = food[
                        (food['Title'] == rec_item['title']) & (food['Index'] == rec_item['index'])]

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
                                switch_to_details(rec_item['title'],
                                                  recommended_food_item['Index'])  # Pass title and index
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

allergen_ingredient_mapping = {
    "Gluten": ["bread", "pasta", "flour", "wheat", "barley", "rye", "bulgur", "farro", "graham", "kamut", "matzo",
           "semolina", "spelt", "triticale", "bran", "spaghetti", "macaroni", "fettuccine", "linguine", "penne"],
    "Peanuts": ["peanuts", "peanut butter", "peanut oil", "groundnut"],
    "Dairy": ["milk", "cheese", "butter", "cream", "yogurt", "buttermilk", "ghee", "whey", "casein", "custard",
              "ice cream"],
    "Soy": ["soy", "soy sauce", "tofu", "tempeh", "edamame", "miso", "soy protein", "soy lecithin", "soya milk"],
    "Eggs": ["eggs", "egg whites", "mayonnaise", "albumin", "meringue", "ovalbumin"],
    "Fish": ["salmon", "tuna", "cod", "haddock", "tilapia", "mackerel", "sardines", "anchovies", "herring", "bass"],
    "Shellfish": ["shrimp", "crab", "lobster", "clams", "oysters", "mussels", "scallops", "prawns", "crawfish",
                  "abalone"],
    "Tree Nuts": ["almonds", "walnuts", "pecans", "cashews", "hazelnuts", "macadamia nuts", "pistachios", "brazil nuts",
                  "pine nuts", "chestnuts"]
}


def food_recommendation_from_precomputed(food, favorite_items=None, top_n=9, selected_allergens=None,
                                         allergen_mapping=None):
    if favorite_items is None:
        favorite_items = []

    if selected_allergens is None:
        selected_allergens = []

    if allergen_mapping is None:
        allergen_mapping = {
            "Gluten": ["bread", "pasta", "flour", "wheat", "barley", "rye", "bulgur", "farro", "graham", "kamut",
                       "matzo", "semolina", "spelt", "triticale", "bran","spaghetti"],
            "Peanuts": ["peanuts", "peanut butter", "peanut oil", "groundnut"],
            "Dairy": ["milk", "cheese", "butter", "cream", "yogurt", "buttermilk", "ghee", "whey", "casein", "custard",
                      "ice cream"],
            "Soy": ["soy", "soy sauce", "tofu", "tempeh", "edamame", "miso", "soy protein", "soy lecithin",
                    "soya milk"],
            "Eggs": ["eggs", "egg whites", "mayonnaise", "albumin", "meringue", "ovalbumin"],
            "Fish": ["salmon", "tuna", "cod", "haddock", "tilapia", "mackerel", "sardines", "anchovies", "herring",
                     "bass"],
            "Shellfish": ["shrimp", "crab", "lobster", "clams", "oysters", "mussels", "scallops", "prawns", "crawfish",
                          "abalone"],
            "Tree Nuts": ["almonds", "walnuts", "pecans", "cashews", "hazelnuts", "macadamia nuts", "pistachios",
                          "brazil nuts", "pine nuts", "chestnuts"]
        }

    all_recommendations = []

    # st.write("Step 1: Adding precomputed recommendations based on favorite items")

    for favorite in favorite_items:
        food_index = favorite['index']  # Extract the index from the favorite dictionary
        # st.write(f"Processing favorite: {favorite['title']} (index: {food_index})")
        if str(food_index) in precomputed_recommendations:
            # st.write(f"Found precomputed recommendations for index {food_index}")
            all_recommendations.extend(precomputed_recommendations[str(food_index)])
        else:
            st.write(f"Warning: No precomputed recommendations found for index {food_index}")

    # print("\n\nfav items"+str(favorite_items))
    # print(precomputed_recommendations["1"])
    # all_recommendations.extend(precomputed_recommendations["1"])
    # print(all)
    # Convert the list of dictionaries to a set of tuples (title, index) for easier comparison
    favorite_set = set((fav['title'], fav['index']) for fav in favorite_items)

    # st.write("Step 2: All collected recommendations (before filtering)")
    # st.write(all_recommendations)

    # Filter out any recommendations that are already in the user's favorites
    filtered_recommendations = [
        rec for rec in all_recommendations
        if (rec['title'], rec['index']) not in favorite_set
    ]

    # Function to check if any allergen-related ingredients are present in the dish
    def contains_allergen_ingredients(ingredients, allergens, allergen_mapping):
        ingredients_lower = [ingredient.lower() for ingredient in ingredients]  # Lowercase all ingredients for comparison
        
        for allergen in allergens:
            related_ingredients = allergen_mapping.get(allergen, [])
            related_ingredients_lower = [ri.lower() for ri in related_ingredients]  # Lowercase all related ingredients
            
            # # Debugging print statements
            # print(f"Checking for allergen: {allergen}")
            # print(f"Ingredients: {ingredients_lower}")
            # print(f"Related ingredients for {allergen}: {related_ingredients_lower}")

            # Check for partial matches in the ingredients list
            for ingredient in ingredients_lower:
                for related in related_ingredients_lower:
                    if related in ingredient:
                        # print(f"Found allergen '{related}' in ingredient '{ingredient}'")
                        return True
        return False


    allergen_free_recommendations = []

    # st.write("Step 4: Filtering recommendations by allergens")
    for rec in filtered_recommendations:
        food_index = rec['index']
        # st.write(f"Checking recommendation: {rec['title']} (index: {rec['index']})")
        if not food.loc[food['Index'] == food_index, 'Ingredients'].empty:
            ingredients = food.loc[food['Index'] == food_index, 'Ingredients'].values[0]
            # st.write(f"Ingredients: {ingredients}")
            # print(selected_allergens)
            # print(f"ingredients: {ingredients}")
            # Check if the ingredients contain any allergens and print the ones being filtered out
            if not contains_allergen_ingredients(ingredients, selected_allergens, allergen_mapping):
                # print(f"Filtered out: {rec['title']} (index: {rec['index']}) due to allergens in: {ingredients}")
                if(rec['title']=="Spaghetti Carbonara with Pork Belly and Fresh Peas"):
                    print(selected_allergens)
                    print(f"\n ingredients{ingredients }\n\n\n")
                    # print(allergen_mapping)
                    print("IT FKIN DOESNT WORK")
                allergen_free_recommendations.append(rec)
        else:
            print(f"Warning: No ingredients found for index {food_index}")

    # Sort and return the unique recommendations
    # st.write("Step 5: Final recommendations after allergen filtering")
    # st.write(filtered_recommendations)

    unique_recommendations = pd.Series(allergen_free_recommendations).value_counts().index.tolist()

    return unique_recommendations[:top_n]


def add_to_favorites(collection, username, food_title, food_index):
    """Add a food item to the user's favorites in MongoDB with the index."""
    # Find the user by username and add the food title along with the index to the favorites list
    food_index = int(food_index)
    collection.update_one(
        {"username": username},
        {"$addToSet": {"favorites": {"title": food_title, "index": food_index}}}  # $addToSet ensures no duplicates
    )


def test_contains_allergen_ingredients():
    allergen_ingredient_mapping = {
        "Gluten": ["bread", "pasta", "flour", "wheat", "barley", "rye", "bulgur", "farro", "graham", "kamut",
                   "matzo", "semolina", "spelt", "triticale", "bran", "spaghetti", "macaroni", "fettuccine", "linguine", "penne"]
    }
    
    # Test case: Ingredients list containing "spaghetti"
    ingredients = [
        '1/2 teaspoon coarse kosher salt',
        '1/2 teaspoon coriander seeds, crushed',
        '1 pound fresh pork belly',
        '1 small onion, quartered',
        '1 small carrot, peeled, quartered',
        '1/2 celery stalk, cut into 2-inch pieces',
        '2 garlic cloves, peeled, smashed',
        '1 bay leaf',
        '1/4 teaspoon whole black peppercorns',
        '2 tablespoons (or more) dry white wine',
        '1/2 cup low-salt chicken broth',
        '2 tablespoons olive oil',
        '1 garlic clove, minced',
        '1/4 cup dry white wine',
        '1 pound spaghetti',  # This should trigger the allergen detection
        '1 1/2 cups fresh shelled peas',
        '2 large eggs',
        '1/2 cup grated Parmesan cheese',
        '1/4 cup grated Pecorino Romano cheese',
        '1/4 cup chopped fresh Italian parsley'
    ]
    
    selected_allergens = ["Gluten"]

    # Function to check if any allergen-related ingredients are present in the dish
    def contains_allergen_ingredients(ingredients, allergens, allergen_mapping):
        ingredients_lower = [ingredient.lower() for ingredient in ingredients]  # Lowercase all ingredients for comparison
        
        for allergen in allergens:
            related_ingredients = allergen_mapping.get(allergen, [])
            related_ingredients_lower = [ri.lower() for ri in related_ingredients]  # Lowercase all related ingredients
            
            # # Debugging print statements
            # print(f"Checking for allergen: {allergen}")
            # print(f"Ingredients: {ingredients_lower}")
            # print(f"Related ingredients for {allergen}: {related_ingredients_lower}")

            # Check for partial matches in the ingredients list
            for ingredient in ingredients_lower:
                for related in related_ingredients_lower:
                    if related in ingredient:
                        print(f"Found allergen '{related}' in ingredient '{ingredient}'")
                        return True
        return False

    # Run the test
    if contains_allergen_ingredients(ingredients, selected_allergens, allergen_ingredient_mapping):
        print("Allergen found: Spaghetti is correctly identified as containing gluten.")
    else:
        print("Allergen not found: There might be an issue with the detection logic.")

# Call the test function
test_contains_allergen_ingredients()
