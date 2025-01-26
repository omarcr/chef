import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from llama_parse import LlamaParse
import os
os.environ["LLMA_CLOUD_API_KEY"] = "my_key"


with open("assets/resume_Jennet_Zamanova.pdf", "rb") as file:
    st.download_button(
        label="Download resume as PDF",
        data = file,
        file_name="resume_Jennet_Zamanova.pdf",
        mime="text/plain",
    )


file = st.file_uploader('Choose your .pdf file to upload', type="pdf")

st.session_state.uploaded_file = file

if file:
    if st.button('Parse Uploaded pdf file (Powered by AI)'):

        doc_parsed = LlamaParse(result_type="markdown",api_key="llx-vXZdRSAELbufIsFwWQClBgAXOWLzANydSev6sppcs2otLj9V", parsing_instruction="Extract the names of the dishes, their ingredients, prices, and the images if available."
                                ).load_data(st.session_state.uploaded_file.getvalue(), extra_info={"file_name": "_"})

        st.write('checkpoint3')
        st.write(doc_parsed)

        st.write(doc_parsed[0].text)

        # doc_parsed = LlamaParse(result_type="markdown",api_key=key_input,
        #                         parsing_instruction=parsingInstruction
        #                     ).load_data(st.session_state.uploaded_file.getvalue(), 
        #                                 extra_info={"file_name": "_"})