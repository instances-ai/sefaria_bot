import streamlit as st

# Custom CSS to style the expanders
st.markdown("""
    <style>
    /* Force the font size of the expander title (Summary) */
    .stExpander .st-emotion-cache-1jvr2fz p {
        font-size: 50px !important;
        color: white;
    }

    /* Style the overall header */
    .stExpander summary {
        background-color: #4CAF50 !important;
        padding: 10px;
        border-radius: 5px;
    }

    /* Target the content inside the expander */
    .stExpander div[data-testid="stExpanderDetails"] {
        background-color: #f9f9f9;
        padding: 20px;

    /* Target the specific input field */
    div[data-testid="stTextInputRootElement"] input {
        background-color: #D3D3D3;  /* Light grey background */
        color: black;  /* Ensure text is readable */
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;  /* Optional: Adds a subtle border */
    }
    </style>
    """, unsafe_allow_html=True)

# Example of using expanders with custom styles
with st.expander("Summary"):
    st.write("This is the summary content.")
    user_input = st.text_input("input")

with st.expander("Advanced Analysis"):
    st.write("This is the advanced analysis content.")
