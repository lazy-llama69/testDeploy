import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

def precompute_recommendations(food, top_n=9):
    # Reset the index to ensure it's sequential
    food = food.reset_index(drop=True)
    
    combined_features = food['Title'] + " " + food['Ingredients']
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(combined_features)
    
    # Check the size of the TF-IDF matrix
    if tfidf_matrix.shape[0] != len(food):
        raise ValueError("Mismatch between TF-IDF matrix size and food DataFrame rows.")

    cosine_sim = cosine_similarity(tfidf_matrix)

    precomputed_recommendations = {}

    for idx, row in food.iterrows():
        similarity_scores = list(enumerate(cosine_sim[idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in similarity_scores if i[0] != idx][:top_n]
        recommendations = [
            {
                "title": food['Title'].iloc[i],
                "index": int(food['Index'].iloc[i])  # Convert int64 to native int
            }
            for i in top_indices
        ]
        precomputed_recommendations[int(row['Index'])] = recommendations  # Convert int64 to native int

    return precomputed_recommendations

def main():
    # Load your dataset
    food = pd.read_csv("input/recipes.csv")
    food.dropna(inplace=True)

    # Reset the index to ensure it aligns correctly
    food = food.reset_index(drop=True)

    # Precompute and save recommendations
    precomputed_recommendations = precompute_recommendations(food, top_n=9)
    with open("precomputed_recommendations.json", "w") as f:
        json.dump(precomputed_recommendations, f)

    print("Precomputed recommendations have been saved to precomputed_recommendations.json")

if __name__ == "__main__":
    main()
