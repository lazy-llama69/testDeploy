import google.generativeai as genai
import os
import requests
import streamlit as st
import random 
import pymongo
import ast
# Can use your own api key or use mine(this seems kinda risky showing others the api key idk HAHAHA)
# gemini_api_key = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=gemini_api_key)
client = pymongo.MongoClient("mongodb+srv://tjsdylan0:kzQPOHODZ95Z6fIh@cluster0.1kbkoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["NyomNyom"]
collection = db["User"]

genai.configure(api_key="AIzaSyAHBdAQOzjZiAXUkWD-TjzymkwDd7kxB5g")
model = genai.GenerativeModel('gemini-1.5-flash')

# Set up your API key and endpoint
API_KEY = "lmwr_sk_vYfaUTPZW6_dI5hVY06YlW0CDKmLDWkZmcqVmJ6Wdqf9DyF2"
endpoint = "https://api.limewire.com/v1/generate-image"# Define the image prompt


# # Check if the request was successful
# if response2.status_code == 200:
#     image_data = response2.content
#     # Save the image
#     open("generated_image.png", "wb") as f:
#         f.write(image_data)
#     print("Image generated and saved as 'generated_image.png'")
# else:
#     print("Failed to generate image:", response2.status_code, response2.text)

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
            st.header(f"{response.text}")
            break
        except Exception as e:
            print(f"Attempt failed: {e}")
            continue

    # Generate the image for the food/meal
    prompt = f"A delectable image of a meal/food with these ingredients: {selected_ingredients}"
    payload = {
        "prompt": prompt,
        "aspect_ratio": "1:1"
    }
    headers = {
        "Content-Type": "application/json",
        "X-Api-Version": "v1",
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    response2 = requests.post(url=endpoint, json=payload, headers=headers)

    if response2.status_code == 200:
        image_data = response2.content
        image_path = "generated_image.png"
        with open(image_path, "wb") as f:
            f.write(image_data)
        st.write("Image generated and saved as 'generated_image.png'")
        if os.path.exists(image_path):
            st.image(image_path, use_column_width=True)
        else:
            st.error("The image file was not found after saving.")
    else:
        st.error(f"Failed to generate image: {response2.status_code}. {response2.json().get('error', 'Unknown error')}")




    # Displays ingredients
    st.markdown("**Ingredients:**")
    for idx, ing in enumerate(selected_ingredients):
        st.markdown(f"{idx+1}. {ing}")

    st.markdown('**Instructions**')
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