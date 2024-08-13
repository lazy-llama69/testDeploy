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

st.title("Welcome to Nyom Nyom!")
st.text("Let us help you decide what to eat today")

st.subheader("What's your preference?")
vegn = st.radio("Vegetables or none!", ["veg", "non-veg"], index=1) 

st.subheader("What Cuisine do you prefer?")
cuisine = st.selectbox("Choose your favourite!", ['Healthy Food', 'Snack', 'Dessert', 'Japanese', 'Indian', 'French',
       'Mexican', 'Italian', 'Chinese', 'Beverage', 'Thai'])

st.subheader("How well do you want the dish to be?")  # RATING
val = st.slider("from poor to the best!", 0, 10)

# Load the food and ratings data only once and store them in session state
if 'food_data' not in st.session_state:
    st.session_state.food_data = pd.read_csv("input/recipes.csv")
    st.session_state.food_data.dropna(inplace=True)

if 'ratings_data' not in st.session_state:
    st.session_state.ratings_data = pd.read_csv("input/ratings.csv")

food = st.session_state.food_data
ratings = st.session_state.ratings_data

# Directory where images are stored
image_directory = 'input/Food Images'

# Initialize session state for selected food
if 'selected_food' not in st.session_state:
    st.session_state.selected_food = None

# Use placeholders to optimize UI updates
content_placeholder = st.empty()

# If a food item is selected, show the detailed view
if st.session_state.selected_food:
    with content_placeholder.container():
        food_item = food[food['Title'] == st.session_state.selected_food].iloc[0]
        
        image_path = os.path.join(image_directory, food_item['Image_Name'] + '.jpg')
        
        if os.path.exists(image_path):
            st.image(image_path, use_column_width=True)
        else:
            st.error(f"Image not found: {image_path}")
        
        st.markdown(f"## {food_item['Title']}")
        st.markdown(f"**Ingredients:** {food_item['Ingredients']}")
        st.markdown(f"**Instructions:** {food_item['Instructions']}")
        
        if st.button("Go back"):
            st.session_state.selected_food = None  # Clear the selected food to go back
            st.rerun()  # Clear the content immediately
else:
    with content_placeholder.container():
        # Create a search bar
        search_term = st.text_input("Search for a food item:")

        # Display results only if a search term is entered
        if search_term:
            # Cache search results to make navigation back faster
            if 'search_results' not in st.session_state or st.session_state.last_search_term != search_term:
                filtered_food = food[food['Title'].str.contains(search_term, case=False, na=False)].head(18)
                st.session_state.search_results = filtered_food
                st.session_state.last_search_term = search_term
            else:
                filtered_food = st.session_state.search_results

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
                        
                        if st.button(f"More details about {row['Title']}", key=row['Title']):
                            st.session_state.selected_food = row['Title']
                            st.rerun()# Clear the content immediately

##### IMPLEMENTING RECOMMENDER ######
dataset = ratings.pivot_table(index='Food_ID', columns='User_ID', values='Rating')
dataset.fillna(0, inplace=True)
csr_dataset = csr_matrix(dataset.values)
dataset.reset_index(inplace=True)

model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
model.fit(csr_dataset)

def food_recommendation(food, food_title, top_n=5):

    # Drop rows with any NaN values
    food.dropna(inplace=True)

    # Combine features into a single string
    food['combined_features'] = food['Title'] + " " + food['Ingredients']

    # Create TF-IDF matrix
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(food['combined_features'])

    # Compute cosine similarity matrix
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Get the index of the food item that matches the given title
    food_index = food[food['Title'] == food_title].index

    if food_index.empty:
        print(f"No food item found with the title: {food_title}")
        return pd.Series(dtype=str)

    # Get similarity scores for all foods with that item
    similarity_scores = list(enumerate(cosine_sim[food_index[0]]))

    # Sort foods by similarity score
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Get top N most similar food indices, excluding the first item (itself)
    top_food_indices = [i[0] for i in similarity_scores if i[0] != food_index[0]][:top_n]

    # Return the recommended food titles
    recommendations = food['Title'].iloc[top_food_indices]
    return recommendations

recommendations = food_recommendation(food, 'Shrimp Creole', top_n=5)
recommendations = recommendations[1:6]
names1 = recommendations.tolist()
