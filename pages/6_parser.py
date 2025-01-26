import streamlit as st

from llama_parse import LlamaParse
import json
import replicate

from openai import OpenAI
from typing import List, Dict

from fatsecret import Fatsecret
import requests

import os


CONSUMER_KEY = st.secrets["CONSUMER_KEY"]
CONSUMER_SECRET = st.secrets["CONSUMER_SECRET"]


fs = Fatsecret(CONSUMER_KEY, CONSUMER_SECRET)

ingredient_client = OpenAI(
    base_url=st.secrets["AZURE_API_BASE"],
    api_key=st.secrets["OPENAI_API_KEY"],
)

def get_ingredients(dish_name: str) -> List[str]:
    try:
        recipes = fs.recipes_search(dish_name)[:5]  # Limit to first 5 recipes
    except Exception as e:
        error_message = f'Error getting recipes (search): {str(e)}\n'
        os.write(1, error_message.encode('utf-8'))
        return """Warnings: Could not get ingredients"""

    all_ingredients = []

    # Iterate through each recipe and collect ingredient descriptions
    for recipe in recipes:
        recipe_info = fs.recipe_get(recipe['recipe_id'])
        if 'ingredients' in recipe_info and 'ingredient' in recipe_info['ingredients']:
            for ingredient in recipe_info['ingredients']['ingredient']:
                if 'ingredient_description' in ingredient:
                    all_ingredients.append(ingredient['ingredient_description'])

    # Send to OpenAI API to process ingredients
    prompt = """Here is a list of ingredients with measurements. Please return only the ingredient names 
    (no measurements or amounts) and remove any duplicates. Return as a simple comma-separated list:

    {}""".format(all_ingredients)

    try:
        response = ingredient_client.chat.completions.create(
            model="gpt-4o",  # or your specific Azure model name
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    except Exception as e:
        error_message = f'Error getting ingredients (openai): {str(e)}\n'
        os.write(1, error_message.encode('utf-8'))
        return """Warning: Could not process ingredients"""

    cleaned_ingredients = response.choices[0].message.content

    return cleaned_ingredients

client = OpenAI(
    base_url=st.secrets["AZURE_API_BASE"],
    api_key=st.secrets["OPENAI_API_KEY"],
)

def analyze_ingredients(ingredients: List[str]) -> Dict:
    system_prompt = """You are a dietary restriction analyzer. Given a list of ingredients, determine if the recipe is:
    - Vegan (no animal products)
    - Vegetarian (no meat but may include dairy/eggs)
    - Gluten-free
    - Lactose-free
    - Safe for nut allergies

    Respond in the following JSON format:
    {
        "Vegan-Friendly": true/false,
        "Vegetarian-Friendly": true/false,
        "Gluten-Free": true/false,
        "Lactose-Free": true/false,
        "Nut-Free": true/false,
        "Warnings": ["list any specific concerns or notes"]
    }"""

    ingredients_text = ", ".join(ingredients)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # or your specific Azure model name
            messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze these ingredients: {ingredients_text}"}
        ],
            response_format={ "type": "json_object" }
        )
    except Exception as e:
        error_message = f'Error analyzing ingredients: {str(e)}\n'
        os.write(1, error_message.encode('utf-8'))
        return """{"Warnings": ["Could not analyze ingredients"]}"""
    
    return response.choices[0].message.content


file = st.file_uploader('Choose your .pdf file to upload', type="pdf")

st.session_state.uploaded_file = file

prompt = """Provide your answer in JSON structure like this: {
    "[0-9]*": {
        "dish_name": "The name of the dish",
        "ingredients": "Ingredients of the dish",
        "price": "Price of the dish",
        "image": "Image of the dish"
    }
}.
"""

if file:
    # Add multiple dietary restriction selector before the parse button
    dietary_options = [
        "Vegan",
        "Vegetarian",
        "Gluten-Free",
        "Lactose-Free",
        "Nut-Free"
    ]
    selected_diets = st.multiselect(
        "Select your dietary restrictions",
        dietary_options,
        default=None,
        help="You can select multiple restrictions"
    )
    
    if st.button('Parse Uploaded pdf file (Powered by AI)'):

        
        doc_parsed = LlamaParse(result_type="markdown",api_key= st.secrets["LLAMA_CLOUD_API_KEY"],
                                complemental_formatting_instruction=prompt
                                ).load_data(st.session_state.uploaded_file.getvalue(), extra_info={"file_name": "_"})
        
        # Display raw parsed text for debugging
        # st.write("Raw parsed text:")
        # st.code(doc_parsed[0].text[:50])
        
        dish_names = doc_parsed[0].text
        
        try:
            if dish_names.startswith('```json'):
                dish_names = dish_names[7:]
            if dish_names.endswith('```'):
                dish_names = dish_names[:-3]
            data = json.loads(dish_names)
            # st.write("Parsed JSON data:")
            
            # Add CSS for grid layout and card styling
            st.markdown("""
            <style>
            .stMarkdown {
                width: 100%;
            }
            .cards-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1rem;
                padding: 1rem;
                width: 100%;
            }
            .dish-card {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 1rem;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                height: 100%;
            }
            .dish-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            }
            .dish-content {
                flex: 1;
            }
            .dish-card img {
                width: 100%;
                max-height: 200px;
                object-fit: cover;
                border-radius: 4px;
                margin-top: 1rem;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Start grid container
            st.write('<div class="cards-grid">', unsafe_allow_html=True)
            
            # Create cards
            for key, dish in data.items():
                # Get ingredients from Fatsecret
                if dish['ingredients'] == "" or dish["dish_name"] == "Gyoza":
                    try:
                        dish['ingredients'] = get_ingredients(dish['dish_name'])
                    except Exception as e:
                        st.write(f"Error getting ingredients for {dish['dish_name']}: {e}")
                # Analyze ingredients for dietary restrictions
                dietary_analysis = json.loads(analyze_ingredients([dish['ingredients']]))
                
                # Skip this dish if it doesn't meet ANY of the selected dietary restrictions
                should_display = True
                if selected_diets:
                    for diet in selected_diets:
                        restriction_key = f"{diet}-Friendly" if diet in ["Vegan", "Vegetarian"] else diet
                        if not dietary_analysis.get(restriction_key, True):
                            should_display = False
                            break
                
                if not should_display:
                    continue
                
                # Get warnings from dietary analysis
                warnings = dietary_analysis.get('Warnings', [])
                warnings_html = "<p></p>"
                if warnings:
                    warnings_html = "<p><strong>⚠️ Warnings:</strong><br>"
                    warnings_html += "<br>".join(f"• {warning}" for warning in warnings)
                    warnings_html += "</p>"
                
                card_html = f"""
                    <div class="dish-card">
                        <div class="dish-content">
                            <h3>{dish['dish_name']}</h3>
                            <p><strong>Ingredients:</strong><br>{dish['ingredients']}</p>
                            <p><strong>Price:</strong> {dish['price']}</p>
                            <p><strong>Dietary Info:</strong><br>
                            {'✅ Vegan' if dietary_analysis.get('Vegan-Friendly') else '❌ Not Vegan'}<br>
                            {'✅ Vegetarian' if dietary_analysis.get('Vegetarian-Friendly') else '❌ Not Vegetarian'}<br>
                            {'✅ Gluten-Free' if dietary_analysis.get('Gluten-Free') else '❌ Contains Gluten'}<br>
                            {'✅ Lactose-Free' if dietary_analysis.get('Lactose-Free') else '❌ Contains Lactose'}<br>
                            {'✅ Nut-Free' if dietary_analysis.get('Nut-Free') else '❌ Contains Nuts'}</p>
                            {warnings_html}
                        </div>
                    </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Add image
                if dish.get('image'):
                    st.image(dish['image'], use_container_width=True)
                else:
                    with st.spinner(f'Generating image for {dish["dish_name"]}...'):
                        REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_KEY"]
                        api = replicate.Client(api_token=REPLICATE_API_TOKEN)
                        output = api.run(
                            "black-forest-labs/flux-dev",
                            input={
                                "prompt": f"A photo of {dish['dish_name']} made of {dish['ingredients']} that costs {dish['price']}",
                                "num_inference_steps": 28,
                                "guidance_scale": 7.5,
                                "model": "schnell",
                            },
                        )
                        generated_img_url = str(output[0])
                        st.image(generated_img_url, use_container_width=True)
                
                # # Close card div
                # st.markdown('</div>', unsafe_allow_html=True)
            
            # Close grid container
            st.write('</div>', unsafe_allow_html=True)

        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON: {str(e)}")
            st.write("Please make sure the parsed text is in valid JSON format")



        # doc_parsed = LlamaParse(result_type="markdown",api_key=key_input,
        #                         parsing_instruction=parsingInstruction
        #                     ).load_data(st.session_state.uploaded_file.getvalue(), 
        #                                 extra_info={"file_name": "_"})