import streamlit as st
import requests
from bs4 import BeautifulSoup

# Sefaria API URL
SEFARIA_API_URL = "https://www.sefaria.org/api/texts/"

# Function to fetch text from Sefaria API (Hebrew)
def he_fetch_text_from_sefaria(ref):
    url = f"{SEFARIA_API_URL}{ref}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hebrew_text_html = data.get('he', [])

        # Joining the list to form a single string before cleaning HTML tags
        hebrew_text = BeautifulSoup(' '.join(hebrew_text_html), "html.parser").get_text(separator=' ')

        # Save to session state
        st.session_state['hebrew_text'] = hebrew_text
        return st.session_state['hebrew_text']
    else:
        st.error("Failed to fetch the text")
        st.session_state['hebrew_text'] = "Failed to fetch the text"
        return st.session_state['hebrew_text']

# Function to fetch text from Sefaria API (English)
def en_fetch_text_from_sefaria(ref):
    url = f"{SEFARIA_API_URL}{ref}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        english_text = data.get('text', [])

        # # Process each verse individually
        # cleaned_verses = []
        # for verse_html in english_text_html:
        #     # Parse each HTML string
        #     soup = BeautifulSoup(verse_html, "html.parser")

        #     # Replace <br> tags with newline characters to preserve line breaks
        #     for br in soup.find_all("br"):
        #         br.replace_with("\n")

        #     # Get the cleaned text for the current verse, preserving line breaks
        #     cleaned_verse = soup.get_text(separator=' ').strip()

        #     # Append the cleaned verse to the list
        #     cleaned_verses.append(cleaned_verse)

        # # Join the cleaned verses with a double newline to maintain paragraph breaks
        # english_text = '\n\n'.join(cleaned_verses)


        # Save to session state
        #st.session_state['english_text'] = english_text_html

        return english_text
    else:
        st.error("Failed to fetch the text")
        st.session_state['english_text'] = "Failed to fetch the text"
        return st.session_state['english_text']

# Streamlit App
st.title("Sefaria Text Fetcher")

# Input reference
ref = st.text_input("Enter the text reference (e.g., Genesis 1:1):")

# Select language
language = st.selectbox("Select Language", ("Hebrew", "English"))

# Fetch and display the text
if st.button("Fetch Text"):
    if language == "Hebrew":
        hebrew_text = he_fetch_text_from_sefaria(ref)
        st.write("### Hebrew Text:")
        st.write(hebrew_text)
    elif language == "English":
        english_text = en_fetch_text_from_sefaria(ref)
        st.write("### English Text:")
        st.write(english_text)
