import streamlit as st
import openai
import uuid
from translation_analysis import fetch_text_from_sefaria, perform_analysis
from dotenv import load_dotenv
import os

# Set the page configuration
st.set_page_config(page_title="Philosophical Ideas Summarizer", layout="wide")

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")
    st.stop()

# Initialize OpenAI client
client = openai.OpenAI(api_key=openai.api_key)


# Generate a unique conversation ID
conversation_id = str(uuid.uuid4())

# UI Elements for the Streamlit app
st.title("Chat with Analysis Bot")

# Get input from user for Sefaria text reference
ref = st.text_input("Enter the text reference in the form 'Book, Chapter' (e.g., Shev_Shmateta, Shmatta 1)", value="Shev_Shmateta, Shmatta 1")

# Initialise session state
st.session_state['empty'] = ''

# Button to fetch and analyze text
if st.button("Fetch and Analyze Text"):
    if ref:
        hebrew_text = fetch_text_from_sefaria(ref)
        if hebrew_text:
            # Store the original text in session state if not already stored
            if 'hebrew_text' not in st.session_state:
                st.session_state['hebrew_text'] = hebrew_text

            # Check if analysis has already been performed and stored in session state
            if 'analysis' not in st.session_state:
                # Perform the analysis and store the results in session state
                analysis_results = perform_analysis(client, conversation_id, st.session_state['hebrew_text'])
                st.session_state['analysis'] = analysis_results
            else:
                analysis_results = st.session_state['analysis']

            # Display the analysis results
            st.header("Hebrew Text")
            st.write(f"<div style='font-family: Noto Sans Hebrew;'>{hebrew_text}</div>", unsafe_allow_html=True)
            st.header("Translation")
            st.write(analysis_results['translation'])
            st.header("1. Overview")
            st.write(analysis_results['overview'])
            st.header("2. Hierarchical Outline")
            st.write(analysis_results['outline'])
            st.header("3. Breakdown of Key Sections")
            st.write(analysis_results['breakdown'])
            st.header("4. Simplifying Challenging Passages")
            st.write(analysis_results['simplify'])
            st.header("5. Concluding Discussion")
            st.write(analysis_results['conclusion'])
            st.write(analysis_results['impact'])
            st.write(analysis_results['criticism'])
            st.write(analysis_results['summary'])
            st.write(analysis_results['flow'])
            st.write(analysis_results['counter'])
            st.write(analysis_results['coherence'])

# Chatbot interaction
if 'analysis' in st.session_state:
    st.header("5.8 Chat with the Analysis")
    user_question = st.text_input("Ask a question about the analysis:")

    if st.button("Ask"):
        if user_question:
            # Combine user's question with the analysis for context
            context = st.session_state['analysis'] + "\n\n" + user_question

            # Call to the OpenAI API to get a response
            response = completion = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Or use another model like "gpt-4"
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": context}
                ]
            )

            # Extract the response text
            chatbot_response = response['choices'][0]['message']['content'].strip()

            # Display the chatbot's response
            st.write(f"**Chatbot:** {chatbot_response}")
