import streamlit as st
import openai
import json
from dotenv import load_dotenv
import os

# Load the API key from the .env file
load_dotenv()
openai.api_key = os.getenv('sk-cF_Rnxd-Xm8h1a6YuTZOET0LnDo4_Ph5xpQiP9dJ2nT3BlbkFJrxQ11hxUiX0AI9V-ZiLAL3QpaTzBewYpjOYIfSDJcA')

# Initialize the Streamlit app
st.set_page_config(page_title="Philosophical Ideas Summarizer", layout="wide")

# Sidebar for customization options
st.sidebar.title("Customization Options")

# Chatbot name and avatar
chatbot_name = st.sidebar.text_input("Chatbot Name", value="Philosopher Bot")
chatbot_avatar = st.sidebar.file_uploader("Upload Avatar", type=["png", "jpg", "jpeg"])

# Color scheme
primary_color = st.sidebar.color_picker("Primary Color", value="#4CAF50")
secondary_color = st.sidebar.color_picker("Secondary Color", value="#FFFFFF")

# Font family and size
font_family = st.sidebar.selectbox("Font Family", ["Arial", "Helvetica", "Times New Roman"])
font_size = st.sidebar.slider("Font Size", 14, 24, value=18)

# Chatbot personality
personality = st.sidebar.selectbox("Chatbot Personality", ["Friendly", "Professional", "Humorous"])

# Knowledge base upload
knowledge_base = st.sidebar.file_uploader("Upload Knowledge Base", type=["txt", "pdf"])

# Save and load configuration
if st.sidebar.button("Save Configuration"):
    config = {
        "chatbot_name": chatbot_name,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "font_family": font_family,
        "font_size": font_size,
        "personality": personality,
    }
    with open("chatbot_config.json", "w") as f:
        json.dump(config, f)
    st.sidebar.success("Configuration saved!")

if st.sidebar.button("Load Configuration"):
    with open("chatbot_config.json", "r") as f:
        config = json.load(f)
    st.sidebar.success("Configuration loaded!")

# Main panel for chatbot interaction
st.title(chatbot_name)
if chatbot_avatar is not None:
    st.image(chatbot_avatar, width=100)

st.markdown(f"""
<style>
    .reportview-container .main .block-container{{
        color: {primary_color};
        font-family: {font_family};
        font-size: {font_size}px;
    }}
</style>
""", unsafe_allow_html=True)

def summarize_text(text):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Summarize the following text in a {personality.lower()} tone:\n\n{text}",
        max_tokens=150
    )
    summary = response.choices[0].text.strip()
    return summary

user_input = st.text_area("Enter text to summarize")
if st.button("Summarize"):
    if user_input:
        summary = summarize_text(user_input)
        st.write(summary)
    else:
        st.write("Please enter text to summarize.")
