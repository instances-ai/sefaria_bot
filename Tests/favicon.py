import streamlit as st
from PIL import Image

# # Inject custom HTML to set the favicon
# st.markdown(f"""
#     <head>
#         <link rel="icon" href="UI/Assets/favicon.ico" type="image/x-icon">
#     </head>
#     """, unsafe_allow_html=True)

# # Your Streamlit app content
#st.title("My Streamlit App with Custom Favicon")

im = Image.open("UI/Assets/favicon.ico")
st.set_page_config(
    page_title="Hello",
    page_icon=im,
    layout="wide",
)
