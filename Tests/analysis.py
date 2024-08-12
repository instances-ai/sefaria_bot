import streamlit as st
import openai
import requests
import json
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import re
import unicodedata
import uuid
import chardet
import fitz  # PyMuPDF

# Set the page configuration first
st.set_page_config(page_title="Philosophical Ideas Summarizer", layout="wide")

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Debugging: Print the API key to check if it's loaded correctly (remove this in production)
#st.write(f"Loaded API Key: {openai_api_key}")

if not openai_api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")
    st.stop()

# Initialize the OpenAI client with the API key
client = openai.OpenAI(api_key=openai_api_key)

# Sefaria API URL
SEFARIA_API_URL = "https://www.sefaria.org/api/texts/"

# Function to fetch text from Sefaria API
def fetch_text_from_sefaria(ref):
    url = f"{SEFARIA_API_URL}{ref}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hebrew_text_html = data.get('he', [])

        # Joining the list to form a single string before cleaning HTML tags
        hebrew_text = BeautifulSoup(' '.join(hebrew_text_html), "html.parser").get_text(separator=' ')

        # Normalize the text to remove special characters
        hebrew_text = unicodedata.normalize('NFKD', hebrew_text)

        # Remove non-breaking spaces and other special characters
        hebrew_text = hebrew_text.replace('\xa0', ' ')

        # Remove non-standard whitespace characters
        hebrew_text = re.sub(r'\s+', ' ', hebrew_text).strip()

        # Remove zero-width spaces and other control characters
        hebrew_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', hebrew_text)

        # Remove any remaining non-printable characters
        hebrew_text = ''.join(c for c in hebrew_text if unicodedata.category(c)[0] != 'C')

        return hebrew_text
    else:
        st.error("Failed to fetch text from Sefaria API")
        return None

# Initialize the conversation history
conversation_history = {}

# General function to call OpenAI API with memory
def call_openai_api_with_memory(conversation_id, role, content, temperature=0.5):
    if conversation_id not in conversation_history:
        conversation_history[conversation_id] = [
            {"role": "system", "content": "Your task is to make a complex philosophical work accessible to students. Always answer in English."}
        ]

    conversation_history[conversation_id].append({"role": role, "content": content})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history[conversation_id],
        max_tokens=1500,
        temperature=temperature
    )

    response_message = completion.choices[0].message.content.strip()
    conversation_history[conversation_id].append({"role": "assistant", "content": response_message})

    return response_message

# Function to translate text using GPT
def translate_text(text,temperature=0.0):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional hebrew translating bot."},
            {"role": "user", "content": f"Translate the following text to english:\n{text}. Translate word for word and do not interpret anything. Aswer only with your translation"}
        ],
        max_tokens=1500,
        temperature=temperature
    )
    translation = completion.choices[0].message.content.strip()
    return translation

# Function to turn text to native speaker level using GPT
def native_text(text, temperature=0.):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional translating bot."},
            {"role": "user", "content": f"Improve the following text to native speaker level:\n{text}. Do not change anything to the meaning. Aswer only with the updated text, do not say anything else"}
        ],
        max_tokens=1500,
        temperature=temperature
    )
    native = completion.choices[0].message.content.strip()
    return native

# 0. Understanding Text
def understand_text(conversation_id, text, temperature=0.5):
    content = f"You are a philosophical bot aiding jewish students understand the Tora. Your task is to make a complex philosophical work accessible to students by creating a clear, concise summary and a structured outline that captures the essence of the text without oversimplifying its core ideas. Please first read the text and undersand it thoroughly. Do not answer anything yet. Here is the text:\n{text}."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 1. Overview of the Text
def overview_text(conversation_id, temperature=0.0):
    content = f"Identify the central philosophical question or problem addressed in the text and give a brief overview in one paragraph."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 2. Hierarchical Outline
def outline_text(conversation_id, temperature=0.0):
    content = f"Create a detailed outline of the text's structure using: 1. Roman Numerals: For main sections (I, II, III, etc.). 2. Capital Letters: For subsections (A, B, C, etc.). 3. Arabic Numerals: For specific points or examples (1, 2, 3, etc.). For each section and subsection always start from a new line. Use numbered list for specific points and examples. Only answer with the outline, do not say anything else."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 3. Breakdown of Key Sections or Arguments
def breakdown_text(conversation_id, temperature=0.5):
    content = f"For each major section you have just outlined do the following: 1. Main Idea: Summarize the main idea in 1-2 sentences. 2. Important Terminology or Concepts: Identify and define any crucial terminology or concepts introduced. 3. Relation to Overall Argument: Explain how this section or argument contributes to the overall thesis of the text."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 4. Simplifying Challenging Passages
def simplify_text(conversation_id, temperature=0.5):
    content = f"Identify particularly challenging passages or ideas and provide simplified explanations to aid understanding. Only answer with the explanations, do not say anything else."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 5. Concluding Discussion
# 5.1. Central Thesis or Conclusion
def conclusion_text(conversation_id, temperature=0.5):
    content = f"Summarize the text's central thesis or conclusion in one paragraph. Only answer with the conclusion, do not say anything else. Do not repeat what you have said before."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 5.2. Impact on Philosophical Thought
def impact_text(conversation_id, temperature=0.5):
    content = f"Discuss the influence of this text on subsequent philosophical thought."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 5.3. Criticisms and Alternative Viewpoints
def criticism_text(conversation_id, temperature=0.5):
    content = f"Now your task will be to present any major criticisms or alternative perspectives on the text. To do this properly, you need to conduct a deep dive into the provided text, concentrating exclusively on its philosophical contentions and the logical architecture underpinning its arguments. Approach this analysis with a critical eye, eschewing any basic introductions to the discussed concepts or unnecessary background information. Your analysis should dissect and summarize the fundamental arguments, laying bare the premises, conclusions, and the logical progression knitting them together. Examine the argumentative structure for logical consistency, coherence, and the use of deductive, inductive reasoning, or any logical inferences drawn within the text. Only give your final answer, do not say what you have done."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 5.3.5. Identify Core Arguments:
def identify_text(conversation_id, temperature=0.5):
    content = f"Extract the primary arguments of this text. Do not answer anything for now. Do not repeat what you have said before."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 5.4. Summarize Core Arguments:
def summary_text(conversation_id, temperature=0.5):
    content = f"Succinctly summarize the primary arguments you have just found, including their foundational premises and derived conclusions. Only answer with the summaries, do not say what you have done.Do not repeat what you have said before."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 5.5. Logical Connections and Flow:
def flow_text(conversation_id, temperature=0.5):
    content = f"Trace and elucidate the logical flow that binds these arguments, noting how each premise builds upon the other and the logical operations employed (e.g., deduction, induction). Do not say what you have done. Do not repeat what you have said before."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 5.6. Counterarguments and Perspectives:
def counter_text(conversation_id, temperature=0.5):
    content = f"If the text engages with counterarguments or presents multiple viewpoints, summarize these discussions and analyze how they integrate into or diverge from the main arguments. Do not say what you have done. Do not repeat what you have said before."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)

# 5.7. Coherence and Persuasiveness Evaluation:
def coherence_text(conversation_id, temperature=0.5):
    content = f"Offer a concise critique of the argumentative structure's coherence and the persuasiveness of the presented arguments, grounded in the logical analysis you have conducted. Do not say what you have done. Do not repeat what you have said before."
    return call_openai_api_with_memory(conversation_id, "user", content, temperature)


# Inject custom CSS to load Google Noto Sans Hebrew font
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Hebrew:wght@400;700&display=swap');

body {
    font-family: 'Noto Sans Hebrew', sans-serif;
}
</style>
"""

# Inject custom CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)

# Initialize the Streamlit app
st.title("Philosophical Ideas Summarizer")

# Generate a unique conversation ID
conversation_id = str(uuid.uuid4())

# Get input from user for Sefaria text reference
ref = st.text_input("Enter the text reference in the form 'Book, Chapter' (e.g., Shev_Shmateta, Shmatta 1)", value="Shev_Shmateta, Shmatta 1")

if st.button("Fetch and Analyze Text"):
    if ref:
        hebrew_text = fetch_text_from_sefaria(ref)
        if hebrew_text:
            st.title("Text")
            st.header("Hebrew Text")
            st.write(f"<div style='font-family: Noto Sans Hebrew;'>{hebrew_text}</div>", unsafe_allow_html=True)
            translation = translate_text(hebrew_text)
            native = native_text(translation)
            st.header("Translation")
            st.write(native)
            st.title("Analysis")
            understand = understand_text(conversation_id, hebrew_text)
            st.header("1. Overview")
            overview = overview_text(conversation_id)
            st.write(overview)
            st.header("2. Hierarchical Outline")
            outline = outline_text(conversation_id)
            st.write(outline)
            st.header("3. Breakdown of Key Sections")
            breakdown = breakdown_text(conversation_id)
            st.write(breakdown)
            st.header("4. Simplifying Challenging Passages")
            simplify = simplify_text(conversation_id)
            st.write(simplify)
            st.header("5. Concluding Discussion")
            st.subheader("5.1. Conclusion")
            conclusion = conclusion_text(conversation_id)
            st.write(conclusion)
            st.subheader("5.2. Impact on Philosophical Thought")
            impact = impact_text(conversation_id)
            st.write(impact)
            st.subheader("5.3. Criticisms and Alternative Viewpoints")
            criticism = criticism_text(conversation_id)
            st.write(criticism)
            identify = identify_text(conversation_id)
            st.subheader("5.4. Summary of Core Arguments:")
            summary = summary_text(conversation_id)
            st.write(summary)
            st.subheader("5.5. Logical Connections:")
            flow = flow_text(conversation_id)
            st.write(flow)
            st.subheader("5.6. Counterarguments and Perspectives:")
            counter = counter_text(conversation_id)
            st.write(counter)
            st.subheader("5.7. Coherence and Persuasiveness Evaluation:")
            coherence = coherence_text(conversation_id)
            st.write(coherence)
    else:
        st.error("Please enter a text reference.")

# Function to handle file upload
def handle_uploaded_file(file):
    if file:
        file_type = file.name.split('.')[-1].lower()
        raw_content = file.read()

        if file_type == 'pdf':
            # Handling PDF file
            pdf_document = fitz.open(stream=raw_content, filetype="pdf")
            content = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                content += page.get_text()
            return content
        else:
            # Handling text file
            result = chardet.detect(raw_content)
            encoding = result['encoding']
            if encoding is None:
                encoding = 'utf-8'  # Fallback encoding
            content = raw_content.decode(encoding)
            return content
    return None

# Sidebar for file upload
st.sidebar.title("Upload Hebrew Text File")
knowledge_base = st.sidebar.file_uploader("Upload Knowledge Base", type=["txt", "pdf"])

if knowledge_base:
    uploaded_file_content = handle_uploaded_file(knowledge_base)
    if uploaded_file_content:
        st.subheader("Uploaded File Content")
        st.write(f"<div style='font-family: Noto Sans Hebrew;'>{uploaded_file_content}</div>", unsafe_allow_html=True)
        conversation_id_uploaded_file = str(uuid.uuid4())
        translation = translate_text(uploaded_file_content)
        native = native_text(translation)
        st.subheader("Translation")
        st.write(native)
        understand = understand_text(conversation_id_uploaded_file, uploaded_file_content)
        st.subheader("1. Overview")
        overview = overview_text(conversation_id_uploaded_file)
        st.write(overview)
        st.subheader("2. Hierarchical Outline")
        outline = outline_text(conversation_id_uploaded_file)
        st.write(outline)
        st.subheader("3. Breakdown of Key Sections")
        breakdown = breakdown_text(conversation_id_uploaded_file)
        st.write(breakdown)
        st.subheader("4. Simplifying Challenging Passages")
        simplify = simplify_text(conversation_id_uploaded_file)
        st.write(simplify)
        st.subheader("5. Concluding Discussion")
        st.subheader("5.1. Conclusion")
        conclusion = conclusion_text(conversation_id_uploaded_file)
        st.write(conclusion)
        st.subheader("5.2. Impact on Philosophical Thought")
        impact = impact_text(conversation_id_uploaded_file)
        st.write(impact)
        st.subheader("5.3. Criticisms and Alternative Viewpoints")
        criticism = criticism_text(conversation_id_uploaded_file)
        st.write(criticism)
        identify = identify_text(conversation_id_uploaded_file)
        st.subheader("5.4. Summary of Core Arguments:")
        summary = summary_text(conversation_id_uploaded_file)
        st.write(summary)
        st.subheader("5.5. Logical Connections:")
        flow = flow_text(conversation_id_uploaded_file)
        st.write(flow)
        st.subheader("5.6. Counterarguments and Perspectives:")
        counter = counter_text(conversation_id_uploaded_file)
        st.write(counter)
        st.subheader("5.7. Coherence and Persuasiveness Evaluation:")
        coherence = coherence_text(conversation_id_uploaded_file)
        st.write(coherence)

