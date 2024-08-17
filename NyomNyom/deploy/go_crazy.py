import google.generativeai as genai
import os
import requests
import streamlit as st
import random 
import pymongo
import ast
import io
from PIL import Image
import requests
# Can use your own api key or use mine(this seems kinda risky showing others the api key idk HAHAHA)
# gemini_api_key = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=gemini_api_key)
client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["NyomNyom"]
collection = db["User"]

genai.configure(api_key="AIzaSyAHBdAQOzjZiAXUkWD-TjzymkwDd7kxB5g")
model = genai.GenerativeModel('gemini-1.5-flash')

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"


def display_crazy_tab(food):
    st.title("GO CRAY CRAY 🎉")
    st.subheader("Lets go wild with some random and fun food choices!")

    # Add a slider to choose a value between 5 and 10
    num_crazy_options = st.slider("How crazy do you want to go? Choose a number of crazy options:", min_value=5, max_value=10, value=5)

    # Add a button to trigger crazy actionsif st.button("Go Crazy! 🤪"):
    st.write(f"Here is a wild and crazy food recommendation with  {num_crazy_options} ingredients!")
    selected_ingredients =[]

    # Ensure doesnt crash cuz some ingredients goofy ah
    while True:
        try:
            for _ in range(num_crazy_options):
                # The given string with the ingredients and other content
                ingredients_str = food.sample(1).iloc[0]["Ingredients"]

                # Extract the first occurrence of a list in the string# Find the part of the string that contains the list
                start_index = ingredients_str.find("[")
                end_index = ingredients_str.find("]") + 1# Extract the substring that represents the list
                ingredients_list_str = ingredients_str[start_index:end_index]

                # Convert the string representation of the list to an actual list
                ingredients_list = ast.literal_eval(ingredients_list_str)
                selected_ingredients.append(random.choice(ingredients_list))
            break
        except Exception as e:
            selected_ingredients.clear()
            print(f"Attempt failed: {e}")  
    


    while True:
        try:
            # Generate food title
            prompt =f"Can you give me a creative and roll of the tongue \
                    food title with these ingredients {selected_ingredients} \
                    give me just only the one food title"
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=1.5,
                ),
            )
            filtered_text = ''.join([char for char in response.text if char.isalnum() or char.isspace()])
            st.header(f"{filtered_text}")
            break
        except Exception as e:
            print(f"Attempt failed: {e}")
            continue




    # Generate the image for the food/meal
    while True:
        try:
            prompt = f"A delectable image of a meal/food with these ingredients: {selected_ingredients}"
            headers = {"Authorization": "Bearer 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"}    
            def query(payload):
                response = requests.post(API_URL, headers=headers, json=payload)
                return response.content
            image_bytes = query({
                "inputs": prompt,
            })
            # You can access the image with PIL.Image for example

            image = Image.open(io.BytesIO(image_bytes))
                
            # Display the image in Streamlit
            st.image(image, use_column_width=True)
            break
        except Exception as e:
            print(e)
            continue


    # Displays ingredients
    st.markdown("**Ingredients:**")
    for idx, ing in enumerate(selected_ingredients):
        st.markdown(f"{idx+1}. {ing}")
    st.markdown("")
    prompt =f"Just give me the prep time and instructions \
            ,give me a somewhat realistic but not too long step by step  \
            instructions to prepare this imaginary meal with ingredients {selected_ingredients} \
            Do not show me the name of the food or anything else "
    instructions = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=1.0,
        ),
    )
    st.markdown(instructions.text)
    # st.balloons()  # Add some fun with balloons# Add more crazy actions as needed
    # st.write("Stay tuned for more crazy features!")