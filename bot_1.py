import streamlit as st
import openai
import requests
import json
from dotenv import load_dotenv
import os

# Load the API key from the .env file or directly set it here
openai.api_key = 'sk-cF_Rnxd-Xm8h1a6YuTZOET0LnDo4_Ph5xpQiP9dJ2nT3BlbkFJrxQ11hxUiX0AI9V-ZiLAL3QpaTzBewYpjOYIfSDJcA'

# Sefaria API URL
SEFARIA_API_URL = "https://www.sefaria.org/api/texts/"

# Function to fetch text from Sefaria API
def fetch_text_from_sefaria(ref):
    url = f"{SEFARIA_API_URL}{ref}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hebrew_text = data.get('he', [])
        english_text = data.get('text', [])
        return ' '.join(hebrew_text), ' '.join(english_text)
    else:
        st.error("Failed to fetch text from Sefaria API")
        return None, None

# Function to summarize text using GPT
def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a summarizer bot."},
            {"role": "user", "content": f"Summarize the following text:\n{text}"}
        ],
        max_tokens=150
    )
    summary = response.choices[0].message['content'].strip()
    return summary

# Initialize the Streamlit app
st.set_page_config(page_title="Philosophical Ideas Summarizer", layout="wide")
st.title("Philosophical Ideas Summarizer")

# Get input from user for Sefaria text reference
ref = st.text_input("Enter the text reference (e.g., 'Shev_Shmateta, Shmatta 1 1')", value="Shev_Shmateta, Shmatta 1 1")

if st.button("Fetch and Analyze Text"):
    if ref:
        hebrew_text, english_text = fetch_text_from_sefaria(ref)
        if hebrew_text or english_text:
            st.subheader("Hebrew Text")
            st.write(hebrew_text)
            st.subheader("English Text")
            st.write(english_text)
            st.subheader("Summary")
            if english_text:
                summary = summarize_text(english_text)
                st.write(summary)
            else:
                st.write("No English text available for summary.")
    else:
        st.error("Please enter a text reference.")

# Function to handle file upload
def handle_uploaded_file(file):
    if file:
        content = file.read().decode("utf-8")
        return content
    return None

# Sidebar for file upload
st.sidebar.title("Upload Hebrew Text File")
knowledge_base = st.sidebar.file_uploader("Upload Knowledge Base", type=["txt", "pdf"])

uploaded_file_content = handle_uploaded_file(knowledge_base)
if uploaded_file_content:
    st.subheader("Uploaded File Content")
    st.write(uploaded_file_content)
    st.subheader("Summary")
    summary = summarize_text(uploaded_file_content)
    st.write(summary)
