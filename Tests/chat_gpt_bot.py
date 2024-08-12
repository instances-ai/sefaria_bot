import streamlit as st
import openai
import os

# Get the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Debugging: Print the API key to check if it's loaded correctly (remove this in production)
#st.write(f"Loaded API Key: {openai_api_key}")

if not openai_api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")
    st.stop()

# Initialize the OpenAI client with the API key
client = openai.OpenAI(api_key=openai_api_key)


# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to display chat history
def display_chat_history():
    for i, (user, bot) in enumerate(st.session_state.chat_history):
        st.write(f"**You:** {user}")
        st.write(f"**Bot:** {bot}")

# Function to handle user input
def handle_user_input():
    if st.session_state.user_input:
        user_message = st.session_state.user_input
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Or use any other model like "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        bot_response = completion.choices[0].message.content.strip()
        st.session_state.chat_history.append((user_message, bot_response))
        st.session_state.user_input = ""  # Clear input field

# User input
st.text_input("You:", key="user_input", on_change=handle_user_input)

# Display chat history
display_chat_history()
