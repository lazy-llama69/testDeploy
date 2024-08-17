import streamlit as st
import pandas as pd
import os
import home, random_page, favorites, go_crazy, cuisines
import pymongo

def main():
    # Initialize MongoDB connection and load data
    client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["NyomNyom"]
    collection = db["User"]

    # Load the food and ratings data only once and store them in session state
    if 'food_data' not in st.session_state:
        st.session_state.food_data = pd.read_csv("input/recipes.csv")
        st.session_state.food_data.dropna(inplace=True)

    food = st.session_state.food_data

    # Directory where images are stored
    image_directory = 'input/Food Images'

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "Random", "Favourites", "GO CRAY CRAY", "Cuisines])


    with tab1:
        home.display_home_tab(collection, image_directory, food)

    with tab2:
        random_page.display_random_tab(food, image_directory)

    with tab3:
        favorites.display_favourites_tab(collection, image_directory, food)

    with tab4:
        go_crazy.display_crazy_tab(food)
                                            
    with tab5:
        cuisines.display_cuisine_tab(collection, image_directory, food)


if __name__ == "__main__":
    main()
