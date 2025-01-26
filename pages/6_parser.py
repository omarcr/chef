import streamlit as st

from llama_parse import LlamaParse
import json
import replicate



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
    
    if st.button('Parse Uploaded pdf file (Powered by AI)'):

        
        doc_parsed = LlamaParse(result_type="markdown",api_key= st.secrets["LLAMA_CLOUD_API_KEY"],
                                complemental_formatting_instruction=prompt
                                ).load_data(st.session_state.uploaded_file.getvalue(), extra_info={"file_name": "_"})

        st.write('checkpoint3')
        
        # Display raw parsed text for debugging
        st.write("Raw parsed text:")
        st.code(doc_parsed[0].text[:50])
        
        dish_names = doc_parsed[0].text
        
        try:
            if dish_names.startswith('```json'):
                dish_names = dish_names[7:]
            if dish_names.endswith('```'):
                dish_names = dish_names[:-3]
            data = json.loads(dish_names)
            st.write("Parsed JSON data:")
            
            # Add CSS for grid layout and card styling
            st.markdown("""
            <style>
            .cards-container {
                display: grid;
                gap: 1rem;
                padding: 1rem;
                grid-template-columns: repeat(1, 1fr);  /* Default for mobile */
            }
            
            /* Medium screens */
            @media (min-width: 640px) {
                .cards-container {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
            
            /* Large screens */
            @media (min-width: 992px) {
                .cards-container {
                    grid-template-columns: repeat(3, 1fr);
                }
            }
            
            /* Extra large screens */
            @media (min-width: 1200px) {
                .cards-container {
                    grid-template-columns: repeat(4, 1fr);
                }
            }
            
            .dish-card {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 1rem;
                height: 100%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                background-color: white;
                display: flex;
                flex-direction: column;
                transition: transform 0.2s ease;
            }
            
            .dish-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            .dish-content {
                flex-grow: 1;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create a container with the grid layout
            st.markdown('<div class="cards-container">', unsafe_allow_html=True)
            
            # Iterate through each dish
            for key, dish in data.items():
                # Create card with flex content
                st.markdown(f"""
                <div class="dish-card">
                    <div class="dish-content">
                        <h3>{dish['dish_name']}</h3>
                        <p><strong>Ingredients:</strong><br>{dish['ingredients']}</p>
                        <p><strong>Price:</strong> {dish['price']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # If there's an image, we need to add it separately
                if dish.get('image'):
                    st.image(dish['image'], use_container_width=True)
                else:
                    REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_KEY"]
                    api = replicate.Client(api_token=REPLICATE_API_TOKEN)
                    output = api.run(
                        "black-forest-labs/flux-dev",
                        input={
                            "prompt": f"A photo of {dish['dish_name']} made of {dish['ingredients']} that costs {dish['price']}",
                            "num_inference_steps": 28, # typically need ~30 for "dev" model. Less steps == faster generation, but the quality is worse
                            "guidance_scale": 7.5,     # how much attention the model pays to the prompt. Try different values between 1 and 50 to see
                            "model": "schnell",        # after fine-tuning you can use "schnell" model to generate images faster. In that case put num_inference_steps=4
                        },

                    )

                    generated_img_url = str(output[0])
                    # st.write(f"Generated image URL: {generated_img_url}")
                    st.image(generated_img_url, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON: {str(e)}")
            st.write("Please make sure the parsed text is in valid JSON format")



        # doc_parsed = LlamaParse(result_type="markdown",api_key=key_input,
        #                         parsing_instruction=parsingInstruction
        #                     ).load_data(st.session_state.uploaded_file.getvalue(), 
        #                                 extra_info={"file_name": "_"})