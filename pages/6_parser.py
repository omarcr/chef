import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from llama_parse import LlamaParse
import os


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
        # st.write(doc_parsed)

        st.write(doc_parsed[0].text)

        # doc_parsed = LlamaParse(result_type="markdown",api_key=key_input,
        #                         parsing_instruction=parsingInstruction
        #                     ).load_data(st.session_state.uploaded_file.getvalue(), 
        #                                 extra_info={"file_name": "_"})