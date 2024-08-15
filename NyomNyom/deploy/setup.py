# setup.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

def precompute_recommendations(food, top_n=9):
    combined_features = food['Title'] + " " + food['Ingredients']
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(combined_features)
    cosine_sim = cosine_similarity(tfidf_matrix)

    precomputed_recommendations = {}

    for idx, title in enumerate(food['Title']):
        similarity_scores = list(enumerate(cosine_sim[idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in similarity_scores if i[0] != idx][:top_n]
        precomputed_recommendations[title] = food['Title'].iloc[top_indices].tolist()

    return precomputed_recommendations

def main():
    # Load your dataset
    food = pd.read_csv("input/recipes.csv")
    food.dropna(inplace=True)

    # Define the specific row to remove
    # Remove the first instance  where 'Title' is "Chopped Salad"
    index_to_remove = food[food['Title'] == "Chopped Salad"].index[0]
    food = food.drop(index_to_remove)

    # Precompute and save recommendations
    precomputed_recommendations = precompute_recommendations(food, top_n=9)
    with open("precomputed_recommendations.json", "w") as f:
        json.dump(precomputed_recommendations, f)

    print("Precomputed recommendations have been saved to precomputed_recommendations.json")

if __name__ == "__main__":
    main()


