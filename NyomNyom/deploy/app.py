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
import os

st.title("Welcome to Nyom Nyom !")
st.text("Let us help you decide what to eat today")
# st.image("foood.jpg")

## nav = st.sidebar.radio("Navigation",["Home","IF Necessary 1","If Necessary 2"])



st.subheader("Whats your preference?")
vegn = st.radio("Vegetables or none!",["veg","non-veg"],index = 1) 

st.subheader("What Cuisine do you prefer?")
cuisine = st.selectbox("Choose your favourite!",['Healthy Food', 'Snack', 'Dessert', 'Japanese', 'Indian', 'French',
       'Mexican', 'Italian', 'Chinese', 'Beverage', 'Thai'])


st.subheader("How well do you want the dish to be?")  #RATING
val = st.slider("from poor to the best!",0,10)

food = pd.read_csv("input/recipes.csv")
ratings = pd.read_csv("input/ratings.csv")
# combined = pd.merge(ratings, food, on='Food_ID')
#ans = food.loc[(food.C_Type == cuisine) & (food.Veg_Non == vegn),['Name','C_Type','Veg_Non']]


# Create a DataFrame
food = pd.DataFrame(food)
food.dropna(inplace=True)
st.subheader("What do you feel like eating today?")
# Create a search bar
search_term = st.text_input("Search for a food item:")
# Directory where images are stored
image_directory = 'input/Food Images'
image_extension = '.jpg'  # Assume all images are .jpg files
# Display results only if a search term is entered
if search_term:
    # Filter the DataFrame based on the search term
    filtered_food = food[food['Title'].str.contains(search_term, case=False, na=False)]

    if not filtered_food.empty:
        # Define the number of cards per row
        N_cards_per_row = 3

        # Display results as cards
        for n_row, row in filtered_food.reset_index().iterrows():
            i = n_row % N_cards_per_row
            if i == 0:
                st.write("---")
                cols = st.columns(N_cards_per_row, gap="large")
            # Draw the card
            with cols[i]:
                # Construct the full image path with extension
                image_path = os.path.join(image_directory, row['Image_Name'] + image_extension)
                
                if os.path.exists(image_path):
                    st.image(image_path, use_column_width=True)
                else:
                    st.error(f"Image not found: {row['Image_Name'] + image_extension}")
                
                st.markdown(f"**{row['Title'].strip()}**")
    else:
        st.write("No results found.")




# ans = combined.loc[(combined.C_Type == cuisine) & (combined.Veg_Non == vegn)& (combined.Rating >= val),['Name','C_Type','Veg_Non']]
# names = ans['Name'].tolist()
# x = np.array(names)
# ans1 = np.unique(x)

# finallist = ""
# bruh = st.checkbox("Choose your Dish")
# if bruh == True:
#     finallist = st.selectbox("Our Choices",ans1)


##### IMPLEMENTING RECOMMENDER ######
dataset = ratings.pivot_table(index='Food_ID',columns='User_ID',values='Rating')
dataset.fillna(0,inplace=True)
csr_dataset = csr_matrix(dataset.values)
dataset.reset_index(inplace=True)

model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
model.fit(csr_dataset)

# def food_recommendation(Food_Name):
#     n = 10
#     FoodList = food[food['Name'].str.contains(Food_Name)]  
#     if len(FoodList):        
#         Foodi= FoodList.iloc[0]['Food_ID']
#         Foodi = dataset[dataset['Food_ID'] == Foodi].index[0]
#         distances , indices = model.kneighbors(csr_dataset[Foodi],n_neighbors=n+1)    
#         Food_indices = sorted(list(zip(indices.squeeze().tolist(),distances.squeeze().tolist())),key=lambda x: x[1])[:0:-1]
#         Recommendations = []
#         for val in Food_indices:
#             Foodi = dataset.iloc[val[0]]['Food_ID']
#             i = food[food['Food_ID'] == Foodi].index
#             Recommendations.append({'Name':food.iloc[i]['Name'].values[0],'Distance':val[1]})
#         df = pd.DataFrame(Recommendations,index=range(1,n+1))
#         return df['Name']
#     else:
#         return "No Similar Foods."
    
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


# display = food_recommendation(food)
#names1 = display['Name'].tolist()

recommendations = food_recommendation(food, 'Shrimp Creole', top_n=5)
recommendations = recommendations[1:6]
names1= recommendations.tolist()

#x1 = np.array(names)
#ans2 = np.unique(x1)
# if bruh == True:
#     bruh1 = st.checkbox("We also Recommend : ")
#     if bruh1 == True:
#         for i in display:
#             st.write(i)
