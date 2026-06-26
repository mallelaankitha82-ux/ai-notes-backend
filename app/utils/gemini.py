import os
from google import genai
from dotenv import load_dotenv

# ==========================
# Load Environment Variables
# ==========================
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# ==========================
# Gemini Client
# ==========================
client = genai.Client(api_key=API_KEY)


# ==========================
# Generate AI Notes
# ==========================
def generate_notes(topic, word_limit=300, language="English"):
    try:
        prompt = f"""
Generate detailed study notes.

Topic:
{topic}

Language:
{language}

Approximate Word Limit:
{word_limit}

Return in this format:

# Title

## Introduction

## Main Concepts

## Key Points

## Conclusion
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        print("Gemini Generate Notes Error:", e)

        return f"""
# {topic}

Language: {language}

## Introduction
This note was generated in fallback mode.

## Main Concepts
Gemini API unavailable.

## Key Points
- Point 1
- Point 2
- Point 3

## Conclusion
Please try again later.
"""


# ==========================
# Summarize PDF/Text
# ==========================
def summarize_text(text):
    try:

        prompt = f"""
You are an expert notes generator.

Read the following PDF carefully.

{text}

Generate the response in this format.

# Notes

## Introduction

## Main Concepts

## Key Points

## Advantages

## Disadvantages

## Applications

## Conclusion

--------------------------------------

# Summary

Write a concise summary.

## Important Points

## Final Conclusion
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        print("Gemini Summary Error:", e)

        return f"""
# Notes

Unable to generate notes.

--------------------------------------

# Summary

Unable to generate summary.

Error:
{str(e)}
"""


# ==========================
# PDF Compatibility
# ==========================
def summarize_pdf_text(text):
    return summarize_text(text)


# ==========================
# Ask Questions From PDF
# ==========================
def ask_pdf_question(pdf_text, question):
    try:

        prompt = f"""
You are an AI assistant.

PDF Content:

{pdf_text}

Question:

{question}

Answer ONLY from the PDF.

If the answer is unavailable in the PDF, reply:

"This information is not available in the uploaded PDF."
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        print("Gemini PDF Question Error:", e)
        return f"Question answering failed: {str(e)}"


# ==========================
# Ask Questions From Notes
# ==========================
def ask_notes_question(notes_text, question):
    try:

        prompt = f"""
You are an AI assistant.

Notes:

{notes_text}

Question:

{question}

Answer ONLY using the notes.

If the answer is unavailable, say so.
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return response.text

    except Exception as e:
        print("Gemini Notes Question Error:", e)
        return f"Question answering failed: {str(e)}"