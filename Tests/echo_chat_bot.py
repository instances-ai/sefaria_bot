import streamlit as st

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
        bot_response = f"You said: {st.session_state.user_input}"  # Simple echo response
        st.session_state.chat_history.append((st.session_state.user_input, bot_response))
        st.session_state.user_input = ""  # Clear input field

# Create input field with session state
st.text_input("You:", key="user_input", on_change=handle_user_input)

# Display chat history
display_chat_history()
