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
from PIL import Image
#from streamlit_extras.app_logo import add_logo
#import chardet
#import fitz  # PyMuPDF





############################ Setting up Page ############################

# Set the page configuration first
im = Image.open("UI/Assets/favicon.ico")
st.set_page_config(page_title="Talmud Analysis Web Tool", page_icon=im,layout="wide")

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]

if not openai_api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")
    st.stop()

# Initialize the OpenAI client with the API key
client = openai.OpenAI(api_key=openai_api_key)

# Initialise session state
if 'interaction' not in st.session_state:
    # Initialize the conversation id
    conversation_id = str(uuid.uuid4())
    st.session_state['conversation_id'] = conversation_id
    # Initialize the conversation history
    conversation_history = {}
    st.session_state['conversation_history'] = conversation_history
    # Switch off
    st.session_state['interaction'] = ''


# Initialize the Streamlit app
#add_logo("../[Sefaria_Bot]_2_UI/Assets/[Sefaria_Bot]_Spait_logo_no_backgound.jpeg", height=300)
st.image("UI/Assets/[Sefaria_Bot]_Spait_logo_no_backgound.jpeg", width=100)


st.title("Talmud Analysis Web Tool")
st.write('')







############################ Functions ############################


# Sefaria API URL
SEFARIA_API_URL = "https://www.sefaria.org/api/texts/"

#@st.cache_data
# Function to fetch text from Sefaria API
def he_fetch_text_from_sefaria(ref):
    url = f"{SEFARIA_API_URL}{ref}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hebrew_text_html = data.get('he', [])

        # Joining the list to form a single string before cleaning HTML tags
        hebrew_text = BeautifulSoup(' '.join(hebrew_text_html), "html.parser").get_text(separator=' ')

        # Normalize the text to remove special characters
        #hebrew_text = unicodedata.normalize('NFKD', hebrew_text)

        # Remove non-breaking spaces and other special characters
        #hebrew_text = hebrew_text.replace('\xa0', ' ')

        # Remove non-standard whitespace characters
        #hebrew_text = re.sub(r'\s+', ' ', hebrew_text).strip()

        # Remove zero-width spaces and other control characters
        #hebrew_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', hebrew_text)

        # Remove any remaining non-printable characters
        #hebrew_text = ''.join(c for c in hebrew_text if unicodedata.category(c)[0] != 'C')

        # Save to session state
        st.session_state['hebrew_text'] = hebrew_text
        return st.session_state['hebrew_text']
    else:
        st.error("Failed to fetch the text")
        st.session_state['hebrew_text'] = "Failed to fetch the text"
        return st.session_state['hebrew_text']

def en_fetch_text_from_sefaria(ref):
    url = f"{SEFARIA_API_URL}{ref}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        english_text_html = data.get('text', [])

        # Joining the list to form a single string before cleaning HTML tags
        english_text = BeautifulSoup(' '.join(english_text_html), "html.parser").get_text(separator=' ')

        # Normalize the text to remove special characters
        #english_text = unicodedata.normalize('NFKD', english_text)

        # Remove non-breaking spaces and other special characters
        #english_text = english_text.replace('\xa0', ' ')

        # Remove non-standard whitespace characters
        #english_text = re.sub(r'\s+', ' ', english_text).strip()

        # Remove zero-width spaces and other control characters
        #english_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', english_text)

        # Remove any remaining non-printable characters
        #english_text = ''.join(c for c in english_text if unicodedata.category(c)[0] != 'C')

        # Save to session state
        st.session_state['english_text'] = english_text
        return st.session_state['english_text']
    else:
        st.error("Failed to fetch the text")
        st.session_state['hebrew_text'] = "Failed to fetch the text"
        return st.session_state['english_text']


# General function to call OpenAI API with memory
def call_openai_api_with_memory(conversation_id, role, content, temperature):
    if conversation_id not in st.session_state['conversation_history']:
        st.session_state['conversation_history'][conversation_id] = [
            {"role": "system", "content": '''#CONTEXT:
You are helping students understand a complex philosophical work by making it more accessible to them.

#ROLE:
You are an English-speaking Jewish Orthodox rabbi.

#RESPONSE GUIDELINES:
- Avoid explicitly stating your role or the task you are performing or shalom
- Always reference the specific text you are working with, if known.
- Encourage questions and discussion to engage the students with the material.
- Avoid excessive use of jargon or technical language that may confuse the students
- Use bold formatting to emphasize important terms and concepts
- God should always be G-d
- Hebrew names should be used (if possible); so Moses is Moshe, Aaron is Aharon
- From the analysis remove anything which implies like we're evaluating the work, that would be inappropriate. It's not for us to judge, just to learn and apply
- The usage in English translations of Moshe or Aharon instead of Moses or Aaron is called transliteration. Transliteration is the process of transferring a word from one alphabet or writing system to another, typically by representing each letter or character with a corresponding one from the target language. In this case, "Moshe" and "Aharon" are transliterations of the Hebrew names "מֹשֶׁה" and "אַהֲרֹן", respectively, using the Latin alphabet. Always transliterate all the names.'''}
        ]

    st.session_state['conversation_history'][conversation_id].append({"role": role, "content": content})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state['conversation_history'][conversation_id],
        max_tokens=1500,
        temperature=temperature
    )

    response_message = completion.choices[0].message.content.strip()
    st.session_state['conversation_history'][conversation_id].append({"role": "assistant", "content": response_message})

    return response_message


# Texts function to call OpenAI API with memory
def texts_call_openai_api_with_memory(conversation_id, role, content, temperature):
    if conversation_id not in st.session_state['conversation_history']:
        st.session_state['conversation_history'][conversation_id] = [
            {"role": "system", "content": '''#CONTEXT:
You are an expert in Jewish texts and the Talmud. Your task is to help students expand their learning and engage in more in-depth analysis of Talmudic texts.

#ROLE:
As a knowledgeable guide and mentor, your role is to suggest related texts from the Talmud for students to study, encouraging them to deepen their understanding and explore new perspectives.

#RESPONSE GUIDELINES:
- Suggest 3-5 related Talmudic texts that will help the student expand their learning
- Provide a brief explanation of how each suggested text relates to the student's current study
- Offer guidance on specific aspects of each text to focus on for more in-depth analysis
- Encourage the student to think critically about the connections between the texts
- Use a friendly and supportive tone to motivate the student in their learning journey

#TALMUD STUDY CRITERIA:
1. Suggested texts should be directly relevant to the student's current area of study
2. Prioritize texts that offer new insights or challenge conventional interpretations
3. Consider the student's level of knowledge when selecting texts
4. Avoid suggesting texts that are too complex or require extensive background knowledge
5. Focus on texts that will stimulate critical thinking and encourage deeper engagement with the material'''}]

    st.session_state['conversation_history'][conversation_id].append({"role": role, "content": content})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state['conversation_history'][conversation_id],
        max_tokens=1500,
        temperature=temperature
    )

    response_message = completion.choices[0].message.content.strip()
    st.session_state['conversation_history'][conversation_id].append({"role": "assistant", "content": response_message})

    return response_message

# Movie function to call OpenAI API with memory
def movie_call_openai_api_with_memory(conversation_id, role, content, temperature):
    if conversation_id not in st.session_state['conversation_history']:
        st.session_state['conversation_history'][conversation_id] = [
            {"role": "system", "content": '''#CONTEXT:
You are an expert in Jewish philosophy and are tasked with explaining a complex Jewish philosophical text to a student who is struggling to understand it. To make the concepts more relatable and easier to grasp, you decide to use a movie metaphor to illustrate the key ideas.

#ROLE:
You will take on the role of a wise and knowledgeable teacher who is skilled at breaking down complex ideas and making them accessible to students. Your goal is to help the student understand the Jewish philosophical text by drawing parallels to a movie they are familiar with.

#RESPONSE GUIDELINES:
1. Begin by identifying the core concepts and themes in the Jewish philosophical text that you want to convey to the student.
2. Choose a movie that shares similar themes or has elements that can be used to illustrate the concepts from the text.
3. Provide a brief summary of the movie's plot and characters, highlighting the relevant aspects that relate to the philosophical text.
4. Draw clear parallels between the movie and the text, explaining how the characters, events, or themes in the movie represent or illuminate the ideas in the philosophical work.
5. Use simple, relatable language and avoid jargon or overly complex terminology.
6. Encourage the student to ask questions and engage with the material by drawing their own connections between the movie and the text.

#JEWISH PHILOSOPHICAL TEXT EXPLANATION CRITERIA:
1. Focus on the most essential and fundamental concepts from the text, rather than getting bogged down in minor details.
2. Use the movie metaphor to make abstract ideas more concrete and relatable.
3. Avoid oversimplifying the text or losing the depth and nuance of the original work.
4. Encourage critical thinking and personal interpretation, rather than presenting a single, definitive explanation.

#RESPONSE FORMAT:
Provide the explanation in clear, concise paragraphs, using italics to highlight key terms or concepts. Use line breaks to separate different sections or ideas, and consider using bullet points to list important parallels or connections between the movie and the philosophical text.'''}]

    st.session_state['conversation_history'][conversation_id].append({"role": role, "content": content})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state['conversation_history'][conversation_id],
        max_tokens=1500,
        temperature=temperature
    )

    response_message = completion.choices[0].message.content.strip()
    st.session_state['conversation_history'][conversation_id].append({"role": "assistant", "content": response_message})

    return response_message

# Song function to call OpenAI API with memory
def song_call_openai_api_with_memory(conversation_id, role, content, temperature):
    if conversation_id not in st.session_state['conversation_history']:
        st.session_state['conversation_history'][conversation_id] = [
            {"role": "system", "content": '''#CONTEXT:
You are a creative songwriter tasked with creating an engaging and educational song about a complex Jewish philosophical text to help students better understand the material.

#ROLE:
As a songwriter, your goal is to create a "cool" and memorable song that effectively communicates the key concepts and ideas from the Jewish philosophical text in a way that resonates with students.

#RESPONSE GUIDELINES:
- Begin with a catchy hook that captures the essence of the philosophical text and draws the listener in
- Use a verse-chorus structure to organize the main ideas and themes of the text
- Employ rhyme, metaphor, and other poetic devices to make the lyrics memorable and engaging
- Break down complex concepts into easy-to-understand language and relatable examples
- Use a chorus that reinforces the central message of the text and is easy for students to remember and sing along with
- Avoid using overly academic or dry language that may alienate or bore the listener
- Aim for a song length of 2-3 minutes to maintain student engagement

#SONG CRITERIA:
1. The song should be educational, effectively conveying the main ideas and concepts of the Jewish philosophical text
2. The song should be engaging and "cool," using creative lyrics, rhyme schemes, and metaphors to capture and hold student attention
3. The song should break down complex ideas into accessible, easy-to-understand language and examples
4. The song should have a memorable hook and chorus that reinforces the central message of the text
5. The song should be an appropriate length (2-3 minutes) to maintain student engagement

#RESPONSE FORMAT:
[SONG TITLE]

Verse 1:
[LYRICS]

Chorus:
[LYRICS]

Verse 2:
[LYRICS]

Chorus:
[LYRICS]

Bridge (optional):
[LYRICS]

Chorus:
[LYRICS]

'''}]

    st.session_state['conversation_history'][conversation_id].append({"role": role, "content": content})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state['conversation_history'][conversation_id],
        max_tokens=1500,
        temperature=temperature
    )

    response_message = completion.choices[0].message.content.strip()
    st.session_state['conversation_history'][conversation_id].append({"role": "assistant", "content": response_message})

    return response_message

# @st.cache_data
# # Function to translate text using GPT
# def translate_native_text(conversation_id, text, temperature=0.5):
#     content = f'''The usage in English translations of Moshe or Aharon instead of Moses or Aaron is called transliteration.

# Transliteration is the process of transferring a word from one alphabet or writing system to another, typically by representing each letter or character with a corresponding one from the target language. In this case, "Moshe" and "Aharon" are transliterations of the Hebrew names "מֹשֶׁה" and "אַהֲרֹן", respectively, using the Latin alphabet.

# This is in contrast to translation, which focuses on conveying the meaning of the word, rather than just its sound or spelling.

# First transliterate the following text to english:\n{text}. Now reformulate your transliteration to englishnative speaker level. Answer only with the native speaker level english text. Do not say anything else, do not say what you have done.'''
#     st.session_state['translation'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['translation']

@st.cache_data
# Summary
def summary_text(conversation_id, ref, temperature=1):
    content = f'''#CONTEXT:
This Section is called 'Summary'.
This is the first section of the entire Jewish Texts analysis journey.
The task is to analyze a given text and provide a brief overview focusing on the central philosophical question or problem addressed in the text: {ref}'


1. Identify the central philosophical question or problem addressed in the text: {ref}'
2. Provide a brief overview of the text in one paragraph.
3. Use emojis throughout the overview to make it more engaging and fun.
4. Avoid using emojis in any further interactions beyond the overview.
5. Answer only with the overview, without adding any additional information or explanations.'''
    st.session_state['summary'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['summary']

# @st.cache_data
# # Summary
# def summary_text(conversation_id, ref, temperature=1):
#     content = f"This Section is called 'Summary'. Identify the central philosophical question or problem addressed in the text {ref}' and give a brief overview in one paragraph. Use emojis throught this section only to make it more fun. Do not use emojis in any further interactions. Only answeer with the overview. Answer only with the backgound information, do not say anything else."
#     st.session_state['summary'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['summary']

@st.cache_data
# Backround Information
def background_text(conversation_id, ref, temperature=1):
    content = f"This Section is called 'Background Information'. Provide some background to the text '{ref}'. Always provide new information, never repeat what you have said i nprevious sections. Answer only with the backgound information, do not say anything else."
    st.session_state['background'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['background']

@st.cache_data
# Breakdown of Key Sections
def breakdown_text(conversation_id, ref, temperature=1):
    content = f"This Section is called 'Breakdown of Key Sections'. Identify key sections or {ref} and for each do the following: 1. Main Idea: Summarize the main idea in 1-2 sentences. 2. Important Terminology or Concepts: Identify and define any crucial terminology or concepts introduced. 3. Relation to Overall Argument: Explain how this section or argument contributes to the overall thesis of the text."
    st.session_state['breakdown'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['breakdown']

@st.cache_data
# Simplifying Challenging Passages
def simplify_text(conversation_id, ref, passage, temperature=1):
    content = f"This is Section is called 'Simplification of Challenging Passages'. The user finds this difficult: {passage} in the text {ref}. Locate the appropriate passage in the text and provide simplified explanations to aid understanding. Only answer with the explanations, do not say anything else."
    st.session_state['simplify'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['simplify']

@st.cache_data
# Identify Core Arguments
def identify_text(conversation_id, ref, temperature=1):
    content = f'''This Section is called 'Identification and Summary of Core Arguments'
    #TASK CRITERIA:
1. Focus on identifying and summarizing the core arguments presented in the text {ref}
2. Provide clear explanations of the reasoning behind each argument
3. Discuss the significance and implications of the arguments in the context of Jewish philosophy
4. Avoid going into excessive detail or tangents unrelated to the core arguments
5. Use clear and concise language that is accessible to readers with varying levels of familiarity with Jewish philosophy
'''
    st.session_state['identify'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['identify']

@st.cache_data
# Logical Connections and Flow
def flow_text(conversation_id, ref, temperature=0.5):
    content = f"This Section is called 'Logical Connections Between Core Arguments'. Trace and elucidate the logical flow that binds the arguments presented in the text {ref}, noting how each premise builds upon the other and the logical operations employed (e.g., deduction, induction). Do not say what you have done. Do not repeat what you have said before."
    st.session_state['flow'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['flow']

@st.cache_data
# Criticize Core Arguments
def criticize_text(conversation_id, ref, temperature=0.5):
    content = f'''This Section is called 'Criticism of Core Arguments'
    #Evaluate Strengths
   - Discuss the strengths of each core argument presented in the text {ref}
   - Consider the logic, evidence, and reasoning used to support the arguments

#Assess Weaknesses
   - Identify any weaknesses or flaws in the core arguments
   - Analyze potential counterarguments or alternative perspectives

#Implications and Significance
   - Discuss the implications of the core arguments within the context of Jewish philosophy
   - Consider the potential impact or significance of the arguments on the field

#JEWISH PHILOSOPHICAL TEXT CRITERIA
    - Focus on the central arguments and claims made by the author
    - Consider the text within the broader context of Jewish philosophical thought
    - Avoid personal opinions or biases; maintain a scholarly and objective tone
    - Use clear and concise language to convey your critical analysis
    - Use bullet points or numbered lists to present key points within each section
    - Use proper formatting for any quotes or references to the original text
    - Maintain a professional and scholarly tone throughout the analysis
'''
    st.session_state['criticism'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['criticism']

@st.cache_data
# Provide Alternative Viewpoints
def counter_text(conversation_id, ref,  temperature=0.5):
    content = f'''This Section is called 'Alternate Viewpoints'
    - Provide at least three alternative viewpoints on the text {ref}, each representing a different school of thought or interpretation method within Jewish philosophy.
- For each viewpoint, explain the key arguments, assumptions, and conclusions drawn from the text.
- Analyze the strengths and weaknesses of each viewpoint, considering factors such as logical consistency, textual evidence, and compatibility with other Jewish teachings.
- Conclude by synthesizing the insights gained from the different viewpoints and offering a balanced, nuanced understanding of the text's meaning and significance.
- Focus on the text's central themes, arguments, and concepts, rather than minor details or tangential issues.
 Consider the text's place within the broader context of Jewish thought and its relationship to other Jewish philosophical works.
- Avoid imposing modern or non-Jewish philosophical frameworks onto the text; instead, strive to understand it on its own terms and within its historical and cultural context.
- Engage with the text critically and analytically, but also with respect and sensitivity to its religious and cultural significance.'''
    st.session_state['counter'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['counter']

@st.cache_data
# Impact on Philosophical Thought
def impact_text(conversation_id, ref, temperature=0.5):
    content = f'''This Section is called 'Impact of the Text on Philosophical Thought'
    #RESPONSE GUIDELINES:
- Analyze how the text {ref} builds upon, challenges, or diverges from existing philosophical traditions
- Discuss the novel contributions the text makes to Jewish philosophical thought
- Examine the broader philosophical implications and significance of the text's ideas
- Evaluate the text's lasting impact and influence on subsequent philosophical works and thinkers
- Offer a critical assessment of the text's strengths, limitations, and potential areas for further exploration

#TASK CRITERIA:
1. Focus on the philosophical content and arguments rather than biographical details of the author
2. Situate the text within the broader context of Jewish philosophical traditions and debates
3. Highlight the text's original insights and contributions to philosophical discourse
4. Use specific examples and passages from the text to support your analysis
5. Avoid excessive jargon and strive for clarity in explaining complex philosophical concepts
6. Maintain an objective and balanced perspective, acknowledging both the text's merits and potential criticisms

#RESPONSE FORMAT:
- Use clear headings and subheadings to organize your analysis
- Provide a brief introduction outlining the text's main themes and arguments
- Dedicate separate sections to discussing the text's philosophical contributions, implications, and impact
- Conclude with a summary of your overall assessment and the text's significance in Jewish philosophical thought'''
    st.session_state['impact'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
    return st.session_state['impact']






############################ Old Functions ############################

# @st.cache_data
# # 0. Understanding Text
# def understand_text(conversation_id, text, temperature=0.5):
#     content = f"You are a philosophical bot aiding jewish students understand the Tora. Your task is to make a complex philosophical work accessible to students by creating a clear, concise summary and a structured outline that captures the essence of the text without oversimplifying its core ideas. We will create this summary together, each new propmt will be a new section. Please first read the text and undersand it thoroughly. Do not answer anything yet. Here is the text:\n{text}."
#     st.session_state['understand'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['understand']

# @st.cache_data
# # 1. Overview of the Text
# def overview_text(conversation_id, temperature=0.0):
#     content = f"This is Section 1: Overview of the Text. Identify the central philosophical question or problem addressed in the text and give a brief overview in one paragraph. Only answeer with the overview"
#     st.session_state['overview'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['overview']

# @st.cache_data
# # 2. Hierarchical Outline
# def outline_text(conversation_id, temperature=0.0):
#     content = f"This is Section 2: Hierarchical Outline. Create a detailed outline of the text's structure using: 1. Roman Numerals: For main sections (I, II, III, etc.). 2. Capital Letters: For subsections (A, B, C, etc.). 3. Arabic Numerals: For specific points or examples (1, 2, 3, etc.). For each section and subsection always start from a new line. Use numbered list for specific points and examples. Only answer with the outline, do not say anything else."
#     st.session_state['outline'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['outline']

# 5. Concluding Discussion
# # 5.1. Central Thesis
# def conclusion_text(conversation_id, temperature=0.5):
#     content = f"From now on we will build the Concluding Discussion. This is Section 5.1: Central Thesis. Summarize the text's central thesis or conclusion in one paragraph. Only answer with the conclusion, do not say anything else. Do not repeat what you have said before."
#     st.session_state['conclusion'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['conclusion']

# 5.4. Summarize Core Arguments:
# def summary_text(conversation_id, temperature=0.5):
#     content = f"This is Section 5.4: Summarize Core Arguments. Succinctly summarize the primary arguments you have just found, including their foundational premises and derived conclusions. Only answer with the summaries, do not say what you have done.Do not repeat what you have said before."
#     st.session_state['summary'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['summary']

# 5.7. Coherence and Persuasiveness Evaluation:
# def coherence_text(conversation_id, temperature=0.5):
#     content = f"This is Section 5.7: Coherence and Persuasiveness Evaluation. Offer a concise critique of the argumentative structure's coherence and the persuasiveness of the presented arguments, grounded in the logical analysis you have conducted. Do not say what you have done. Do not repeat what you have said before."
#     st.session_state['coherence'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['coherence']

# @st.cache_data
# # Criticisms and Alternative Viewpoints
# def criticism_text(conversation_id, ref, temperature=0.5):
#     content = f"This is Section 5.3: Criticisms and Alternative Viewpoints. Now your task will be to present any major criticisms or alternative perspectives on the text. To do this properly, you need to conduct a deep dive into the provided text, concentrating exclusively on its philosophical contentions and the logical architecture underpinning its arguments. Approach this analysis with a critical eye, eschewing any basic introductions to the discussed concepts or unnecessary background information. Your analysis should dissect and summarize the fundamental arguments, laying bare the premises, conclusions, and the logical progression knitting them together. Examine the argumentative structure for logical consistency, coherence, and the use of deductive, inductive reasoning, or any logical inferences drawn within the text. Only give your final answer, do not say what you have done."
#     st.session_state['criticism'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['criticism']

# @st.cache_data
# # Counterarguments and Perspectives:
# def counter_text(conversation_id, ref,  temperature=0.5):
#     content = f"This is Section 5.6: Counterarguments and Perspectives. If the text engages with counterarguments or presents multiple viewpoints, summarize these discussions and analyze how they integrate into or diverge from the main arguments. Do not say what you have done. Do not repeat what you have said before."
#     st.session_state['counter'] = call_openai_api_with_memory(conversation_id, "user", content, temperature)
#     return st.session_state['counter']






############################ Chatbot ############################

# Ensure chat history and starter visibility are initialized only once
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    st.session_state['prv_user_question'] = ''
if 'show_starters' not in st.session_state:
    st.session_state['show_starters'] = True

# Sidebar Chatbot UI
st.sidebar.header("Copilot 💬")
user_question = st.sidebar.text_input("Please ask a question related to the text, its translation, or the analysis:")

# Handle the main chat interaction when Enter is pressed
if user_question != st.session_state['prv_user_question']: #and st.session_state['show_starters'] is False:
    chatbot_response = call_openai_api_with_memory(st.session_state['conversation_id'], 'user', user_question, 0.5)
    st.session_state['chat_history'].append((f"**User:** {user_question}", f"**Chatbot:** {chatbot_response}"))
    st.session_state['show_starters'] = False  # Hide starters after first interaction
    st.session_state['prv_user_question'] = user_question
    #st.sidebar.text_input("Ask a question:", key="reset", value="")  # Clear the input field

#st.sidebar.write('')

# Display conversation starter buttons if they should be shown
if st.session_state['show_starters']:
    st.sidebar.write('Get started with an example below:')
    col1, col2, col3 = st.sidebar.columns(3)

    with col1:
        if st.button("Suggest a related text"):
            chatbot_response = texts_call_openai_api_with_memory(st.session_state['conversation_id'], 'user', 'Suggest a related text to {ref} to study', 0.5)
            st.session_state['chat_history'].append((f"**User:** Suggest a related text to {ref} to study", f"**Chatbot:** {chatbot_response}"))
            st.session_state['show_starters'] = False
            st.rerun()

    with col2:
        if st.button("Turn the text into a movie"):
            chatbot_response = movie_call_openai_api_with_memory(st.session_state['conversation_id'], 'user', 'First ask the user what is his favorite movie. Then turn the text into this movie', 1)
            st.session_state['chat_history'].append((f"**User:** Turn the text into a movie", f"**Chatbot:** {chatbot_response}"))
            st.session_state['show_starters'] = False
            st.rerun()

    with col3:
        if st.button("Turn the text into a song"):
            chatbot_response = song_call_openai_api_with_memory(st.session_state['conversation_id'], 'user', 'Trun the text into a song', 1)
            st.session_state['chat_history'].append((f"**User:** Trun the text into a song", f"**Chatbot:** {chatbot_response}"))
            st.session_state['show_starters'] = False
            st.rerun()

# Display the chat history
for question, response in reversed(st.session_state['chat_history']):
    st.sidebar.write(question)
    st.sidebar.write(response)







# ############################ Chatbot ############################

# import streamlit as st

# # Ensure chat history is initialized only once
# if 'chat_history' not in st.session_state:
#     st.session_state['chat_history'] = []

# # Sidebar Chatbot UI
# st.sidebar.header("Copilot")
# user_question = st.sidebar.text_input("Ask a question:")

# # Create two columns for the buttons in the main layout
# col1, col2, col3 = st.sidebar.columns(3)

# with col1:
#     text_button = st.button("Suggest a related text to study")

# with col2:
#     movie_button = st.button("Turn the text into a movie")

# with col3:
#     song_button = st.button("Turn the text into a song")

# if text_button and user_question:
#     chatbot_response = call_openai_api_with_memory(st.session_state['conversation_id'], 'user', user_question, 0.5)
#     st.session_state['chat_history'].append((f"**User:** {user_question}", f"**Chatbot:** {chatbot_response}"))

# if ask2_button and user_question:
#     chatbot_response = call_openai_api_with_memory(st.session_state['conversation_id'], 'user', user_question, 0.5)
#     st.session_state['chat_history'].append((f"**User:** {user_question}", f"**Chatbot:** {chatbot_response}"))

# # Display the chat history
# for question, response in reversed(st.session_state['chat_history']):
#     st.sidebar.write(question)
#     st.sidebar.write(response)










############################ Fetch and Translate ############################

# Get input from user for Sefaria text reference
#ref = st.text_input("Enter the text reference in the form 'Book, Chapter' (e.g., Shev_Shmateta, Shmatta 1)", value="Shev_Shmateta, Shmatta 1")

st.header("Choose your Text 📖")

if 'Fetch' not in st.session_state:
    st.session_state['Fetch'] = False
    st.session_state['ref'] = ''

# if 'translation' not in st.session_state:
#     #st.session_state['Fetch'] = ''
#     #st.session_state['hebrew_text'] = ''
#     st.session_state['translation'] = ''
#     st.session_state['ref'] = ''
#     #st.session_state['Text'] = ''
#     #st.session_state['Translation'] = ''

# Create two columns
col1, col2, col3, col4, col5, col6 = st.columns(6)

# Add content to the first column
with col1:
    book = st.selectbox(
    "Book",
    ("Shev Shmateta", "Tikkunei Zohar", "Genesis"),)

with col2:
    chapter = st.text_input("Chapter number")


if book == 'Tikkunei Zohar' and 'a' not in chapter and 'b' not in chapter and 'c' not in chapter:
    ref = 'Tikkunei_Zohar'+', '+chapter+'a'
else:
    ref = 'Tikkunei_Zohar'+', '+chapter

if book == 'Shev Shmateta':
    ref = 'Shev_Shmateta'+', '+'Shmatta '+chapter

if book == 'Genesis':
    ref = 'Genesis'+', '+chapter

#with col1:
if st.button("Fetch and Translate"):
        #st.write(ref)  # Debugging: Check if the button press is registered
        if ref != st.session_state['ref']:
            st.session_state['summary_expander_open'] = False
            st.session_state['summary'] = ''
            st.session_state['background_expander_open'] = False
            st.session_state['background'] = ''
            st.session_state['breakdown_expander_open'] = False
            st.session_state['breakdown'] = ''
            st.session_state['simplify_expander_open'] = False
            st.session_state['simplify'] = ''
            st.session_state['identify_expander_open'] = False
            st.session_state['identify'] = ''
            st.session_state['flow_expander_open'] = False
            st.session_state['flow'] = ''
            st.session_state['criticism_expander_open'] = False
            st.session_state['criticism'] = ''
            st.session_state['counter_expander_open'] = False
            st.session_state['counter'] = ''
            st.session_state['impact_expander_open'] = False
            st.session_state['impact'] = ''
            st.session_state['show_starters'] = True
            st.session_state['Fetch']  = True

        #if ref:
            he_fetch_text_from_sefaria(ref)
            en_fetch_text_from_sefaria(ref)
            #translate_native_text(st.session_state['conversation_id'], st.session_state['hebrew_text'])
            st.session_state['ref']  = ref
            #st.session_state['Text'] = 'Text'
            #st.session_state['Translation'] = 'Translation'
        st.rerun()


# Create two columns
col1, col2 = st.columns(2)

# Add content to the first column
with col1:
    #if st.session_state['translation']  != '':
        if st.session_state['Fetch']  == True:
            st.subheader('Text 📜')
            if st.session_state['hebrew_text'] == '':
                st.write('The API failed, please try again')
            else:
                st.write(f"<div style='font-family: Noto Sans Hebrew;'>{st.session_state['hebrew_text']}</div>", unsafe_allow_html=True)


# Add content to the second column
with col2:
    #if st.session_state['translation']  != '':
        if st.session_state['Fetch']  == True:
            st.subheader('Translation 🌐')
            if st.session_state['hebrew_text'] == '':
                st.write('')
            else:
                st.write(st.session_state['english_text'])





############################ Summary and Background ############################
st.header("Summary and Background 📚")

if 'summary' not in st.session_state:
    #st.session_state['Summary'] = ''
    st.session_state['summary'] = ''
    st.session_state['summary_expander_open'] = False

with st.expander("Summary", expanded=st.session_state['summary_expander_open']):
    #st.write(st.session_state['summary_expander_open'])
    if st.session_state['summary'] == '':
        st.write('')
        if st.button("Summarize"):
            st.session_state['summary_expander_open'] = True
            summary = summary_text(st.session_state['conversation_id'], ref)
            #st.write('Button 1 pressed')
            st.rerun()
    col1sum, col2sum, col3sum = st.columns([0.3, 0.7, 0.3])
    with col2sum:
        st.write('')
        st.write(st.session_state['summary'])



#######


if 'background' not in st.session_state:
    #st.session_state['Background'] = ''
    st.session_state['background'] = ''
    st.session_state['background_expander_open'] = False

with st.expander("Background Information", expanded=st.session_state['background_expander_open']):
    if st.session_state['background'] == '':
        st.write('')
        if st.button("Get Backgound Information"):
            st.session_state['background_expander_open'] = True
            background = background_text(st.session_state['conversation_id'], ref)
            st.rerun()
    col1back, col2back, col3back = st.columns([0.3, 0.7, 0.3])
    with col2back:
        st.write('')
        st.write(st.session_state['background'])
    #st.write('background')






############################ Analysis ############################

st.header("Advanced Analysis 🔍")


if 'breakdown' not in st.session_state:
    #st.session_state['Key_Sections'] = ''
    st.session_state['breakdown'] = ''
    st.session_state['breakdown_expander_open'] = False

with st.expander("Breakdown of Key Sections", expanded=st.session_state['breakdown_expander_open']):
    if st.session_state['breakdown'] == '':
        st.write('')
        if st.button("Breakdown Key Sections"):
            st.session_state['breakdown_expander_open'] = True
            breakdown = breakdown_text(st.session_state['conversation_id'], ref)
            st.rerun()
    col1break, col2break, col3break = st.columns([0.3, 0.7, 0.3])
    with col2break:
        st.write('')
        st.write(st.session_state['breakdown'])
    #st.write('background')


#######


if 'simplify' not in st.session_state:
    #st.session_state['Challenging_Passages'] = ''
    st.session_state['simplify'] = ''
    st.session_state['simplify_expander_open'] = False

with st.expander("Simplification of Challenging Passages", expanded=st.session_state['simplify_expander_open']):
    col1simp, col2simp, col3simp = st.columns([0.3, 0.7, 0.3])
    #st.write('here')
    with col1simp:
        st.write('')
        st.write('What passage do you find difficult?')
        passage = st.text_input('.',label_visibility="collapsed")
        if st.button("Simplify"):
            st.session_state['simplify_expander_open'] = True
            simplify = simplify_text(st.session_state['conversation_id'], ref, passage)
            st.rerun()
    with col2simp:
        st.write('')
        st.write(st.session_state['simplify'])



#######


if 'identify' not in st.session_state:
    #st.session_state['Core_Arguments'] = ''
    st.session_state['identify'] = ''
    st.session_state['identify_expander_open'] = False

with st.expander("Identification and Summary of Core Arguments", expanded=st.session_state['identify_expander_open']):
    if st.session_state['identify'] == '':
        st.write('')
        if st.button("Get Core Arguments"):
            st.session_state['identify_expander_open'] = True
            identify = identify_text(st.session_state['conversation_id'], ref)
            st.rerun()
    col1ident, col2ident, col3ident = st.columns([0.3, 0.7, 0.3])
    with col2ident:
        st.write('')
        st.write(st.session_state['identify'])


#######


if 'flow' not in st.session_state:
    #st.session_state['Logical Connections'] = ''
    st.session_state['flow'] = ''
    st.session_state['flow_expander_open'] = False

with st.expander("Logical Connections Between Core Arguments ", expanded=st.session_state['flow_expander_open']):
    if st.session_state['flow'] == '':
        st.write('')
        if st.button("Draw Logical Connections"):
            st.session_state['flow_expander_open'] = True
            flow = flow_text(st.session_state['conversation_id'], ref)
            st.rerun()
    col1flow, col2flow, col3flow = st.columns([0.3, 0.7, 0.3])
    with col2flow:
        st.write('')
        st.write(st.session_state['flow'])



#######


if 'criticism' not in st.session_state:
    #st.session_state['Logical Connections'] = ''
    st.session_state['criticism'] = ''
    st.session_state['criticism_expander_open'] = False

with st.expander("Criticism of Core Arguments", expanded=st.session_state['criticism_expander_open']):
    if st.session_state['criticism'] == '':
        st.write('')
        if st.button("Criticize Core Arguments"):
            st.session_state['criticism_expander_open'] = True
            criticism = criticize_text(st.session_state['conversation_id'], ref)
            st.rerun()
    col1crit, col2crit, col3crit = st.columns([0.3, 0.7, 0.3])
    with col2crit:
        st.write('')
        st.write(st.session_state['criticism'])


#######


if 'counter' not in st.session_state:
    #st.session_state['Logical Connections'] = ''
    st.session_state['counter'] = ''
    st.session_state['counter_expander_open'] = False

with st.expander("Alternative Viewpoints", expanded=st.session_state['counter_expander_open']):
    if st.session_state['counter'] == '':
        st.write('')
        if st.button("Provide Alternative Viewpoints"):
            st.session_state['counter_expander_open'] = True
            counter = counter_text(st.session_state['conversation_id'], ref)
            st.rerun()
    col1counter, col2counter, col3counter = st.columns([0.3, 0.7, 0.3])
    with col2counter:
        st.write('')
        st.write(st.session_state['counter'])

#######


if 'impact' not in st.session_state:
    #st.session_state['Logical Connections'] = ''
    st.session_state['impact'] = ''
    st.session_state['impact_expander_open'] = False

with st.expander("Impact of the Text on Philosophical Thought", expanded=st.session_state['impact_expander_open']):
    if st.session_state['impact'] == '':
        st.write('')
        if st.button("Get Impact"):
            st.session_state['impact_expander_open'] = True
            impact = impact_text(st.session_state['conversation_id'], ref)
            st.rerun()
    col1impact, col2impact, colimpact = st.columns([0.3, 0.7, 0.3])
    with col2impact:
        st.write('')
        st.write(st.session_state['impact'])


############################ CSS ############################

# Inject custom CSS for fonts
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Hebrew:wght@400;700&display=swap');

body {
    font-family: 'Noto Sans Hebrew', sans-serif;
}
</style>
"""

# Inject the custom CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)

# Custom CSS to style the expanders
st.markdown("""
    <style>
    /* Force the font size of the expander title (Summary) */
    .stExpander .st-emotion-cache-1jvr2fz p {
        font-size: 20px !important;
        color: black;
    }

    /* Style the overall header */
    .stExpander summary {
        background-color: rgba(54,112,161,0.2) !important;
        padding: 10px;
        border-radius: 5px;
    }


    * Target the specific input field */
    div[data-testid="stTextInputRootElement"] input {
        background-color: #D3D3D3;  /* Light grey background */
        color: black;  /* Ensure text is readable */
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;  /* Optional: Adds a subtle border */

    }
    </style>
    """, unsafe_allow_html=True)

    # /* Target the content inside the expander */
    # .stExpander div[data-testid="stExpanderDetails"] {
    #     padding: 20px;
    #     background-color: white;


# # Inject JavaScript to scroll to the bottom of the page with a delay
# js = f"""
# <script>
#     function scroll(dummy_var_to_force_repeat_execution){{
#         var textAreas = parent.document.querySelectorAll('section.main');
#         setTimeout(function() {{
#             for (let index = 0; index < textAreas.length; index++) {{
#                 textAreas[index].scrollTop = textAreas[index].scrollHeight;
#             }}
#         }}, 500);  // Adjust the delay as needed (500 milliseconds)
#     }}
#     scroll({len(st.session_state['interaction'])})
# </script>
# """

# # Execute the JavaScript in the app
# st.components.v1.html(js, height=0)


