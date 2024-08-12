import openai
import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import json
from dotenv import load_dotenv
import os


# Function to fetch text from Sefaria API
def fetch_text_from_sefaria(ref):
    SEFARIA_API_URL = "https://www.sefaria.org/api/texts/"
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
        return "Failed to fetch text from Sefaria API"

# Initialize the conversation history
conversation_history = {}

# General function to call OpenAI API with memory
def call_openai_api_with_memory(client, conversation_id, role, content, temperature=0.5):
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
def translate_text(client, text,temperature=0.0):
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
def native_text(client, text, temperature=0.):
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
def understand_text(client, conversation_id, text, temperature=0.5):
    content = f"You are a philosophical bot aiding jewish students understand the Tora. Your task is to make a complex philosophical work accessible to students by creating a clear, concise summary and a structured outline that captures the essence of the text without oversimplifying its core ideas. Please first read the text and undersand it thoroughly. Do not answer anything yet. Here is the text:\n{text}."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 1. Overview of the Text
def overview_text(client, conversation_id, temperature=0.0):
    content = f"Identify the central philosophical question or problem addressed in the text and give a brief overview in one paragraph."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 2. Hierarchical Outline
def outline_text(client, conversation_id, temperature=0.0):
    content = f"Create a detailed outline of the text's structure using: 1. Roman Numerals: For main sections (I, II, III, etc.). 2. Capital Letters: For subsections (A, B, C, etc.). 3. Arabic Numerals: For specific points or examples (1, 2, 3, etc.). For each section and subsection always start from a new line. Use numbered list for specific points and examples. Only answer with the outline, do not say anything else."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 3. Breakdown of Key Sections or Arguments
def breakdown_text(client, conversation_id, temperature=0.5):
    content = f"For each major section you have just outlined do the following: 1. Main Idea: Summarize the main idea in 1-2 sentences. 2. Important Terminology or Concepts: Identify and define any crucial terminology or concepts introduced. 3. Relation to Overall Argument: Explain how this section or argument contributes to the overall thesis of the text."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 4. Simplifying Challenging Passages
def simplify_text(client, conversation_id, temperature=0.5):
    content = f"Identify particularly challenging passages or ideas and provide simplified explanations to aid understanding. Only answer with the explanations, do not say anything else."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 5. Concluding Discussion
# 5.1. Central Thesis or Conclusion
def conclusion_text(client, conversation_id, temperature=0.5):
    content = f"Summarize the text's central thesis or conclusion in one paragraph. Only answer with the conclusion, do not say anything else. Do not repeat what you have said before."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 5.2. Impact on Philosophical Thought
def impact_text(client, conversation_id, temperature=0.5):
    content = f"Discuss the influence of this text on subsequent philosophical thought."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 5.3. Criticisms and Alternative Viewpoints
def criticism_text(client, conversation_id, temperature=0.5):
    content = f"Now your task will be to present any major criticisms or alternative perspectives on the text. To do this properly, you need to conduct a deep dive into the provided text, concentrating exclusively on its philosophical contentions and the logical architecture underpinning its arguments. Approach this analysis with a critical eye, eschewing any basic introductions to the discussed concepts or unnecessary background information. Your analysis should dissect and summarize the fundamental arguments, laying bare the premises, conclusions, and the logical progression knitting them together. Examine the argumentative structure for logical consistency, coherence, and the use of deductive, inductive reasoning, or any logical inferences drawn within the text. Only give your final answer, do not say what you have done."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 5.3.5. Identify Core Arguments:
def identify_text(client, conversation_id, temperature=0.5):
    content = f"Extract the primary arguments of this text. Do not answer anything for now. Do not repeat what you have said before."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 5.4. Summarize Core Arguments:
def summary_text(client, conversation_id, temperature=0.5):
    content = f"Succinctly summarize the primary arguments you have just found, including their foundational premises and derived conclusions. Only answer with the summaries, do not say what you have done.Do not repeat what you have said before."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 5.5. Logical Connections and Flow:
def flow_text(client, conversation_id, temperature=0.5):
    content = f"Trace and elucidate the logical flow that binds these arguments, noting how each premise builds upon the other and the logical operations employed (e.g., deduction, induction). Do not say what you have done. Do not repeat what you have said before."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 5.6. Counterarguments and Perspectives:
def counter_text(client, conversation_id, temperature=0.5):
    content = f"If the text engages with counterarguments or presents multiple viewpoints, summarize these discussions and analyze how they integrate into or diverge from the main arguments. Do not say what you have done. Do not repeat what you have said before."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)

# 5.7. Coherence and Persuasiveness Evaluation:
def coherence_text(client, conversation_id, temperature=0.5):
    content = f"Offer a concise critique of the argumentative structure's coherence and the persuasiveness of the presented arguments, grounded in the logical analysis you have conducted. Do not say what you have done. Do not repeat what you have said before."
    return call_openai_api_with_memory(client, conversation_id, "user", content, temperature)


# Define the analysis functions here
def perform_analysis(client, conversation_id, hebrew_text):
    translation = translate_text(client, hebrew_text)
    native_translation = native_text(client, translation)

    # Perform other analyses and return results
    overview = overview_text(client, conversation_id)
    outline = outline_text(client, conversation_id)
    breakdown = breakdown_text(client, conversation_id)
    simplify = simplify_text(client, conversation_id)
    conclusion = conclusion_text(client, conversation_id)
    impact = impact_text(client, conversation_id)
    criticism = criticism_text(client, conversation_id)
    summary = summary_text(client, conversation_id)
    flow = flow_text(client, conversation_id)
    counter = counter_text(client, conversation_id)
    coherence = coherence_text(client, conversation_id)

    return {
        'translation': native_translation,
        'overview': overview,
        'outline': outline,
        'breakdown': breakdown,
        'simplify': simplify,
        'conclusion': conclusion,
        'impact': impact,
        'criticism': criticism,
        'summary': summary,
        'flow': flow,
        'counter': counter,
        'coherence': coherence
    }

