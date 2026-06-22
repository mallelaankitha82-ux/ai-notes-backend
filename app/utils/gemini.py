import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_notes(topic: str, words: int = 300, language: str = "English"):
    try:
        prompt = f"""
Generate detailed notes on {topic}
in approximately {words} words.

IMPORTANT:
Write the entire response in {language} language.

Give:
- Heading
- Introduction
- Main Points
- Conclusion
"""
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"# {topic}\n\nGemini Error: {str(e)}"


def summarize_pdf_text(text: str, language: str = "English"):
    try:
        prompt = f"""
Summarize the following content.

Language: {language}

{text[:10000]}
"""
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"PDF Summary Error: {str(e)}"


def ask_pdf_question(pdf_text: str, question: str):
    try:
        prompt = f"""
Based on the following PDF content:

{pdf_text}

Answer this question:

{question}
"""
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Gemini Error: {str(e)}"


def ask_notes_question(notes_text: str, question: str):
    try:
        prompt = f"""
Notes Content:

{notes_text}

Question:

{question}

Answer only from the notes content.
"""
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Gemini Error: {str(e)}"

