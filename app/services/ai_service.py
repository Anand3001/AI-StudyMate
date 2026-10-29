
from pathlib import Path
from dotenv import dotenv_values
from groq import Groq

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


def get_groq_client():
    config = dotenv_values(ENV_FILE)
    api_key = (config.get("GROQ_API_KEY") or "").strip()

    if not api_key:
        raise ValueError(
            f"GROQ_API_KEY is missing or empty in: {ENV_FILE}"
        )

    return Groq(api_key=api_key)


def generate_summary(pdf_text, max_words=250):
    if not pdf_text or not pdf_text.strip():
        raise ValueError("PDF text is empty.")

    config = dotenv_values(ENV_FILE)
    model = (
        config.get("GROQ_MODEL") or "openai/gpt-oss-120b"
    ).strip()

    client = get_groq_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an academic study assistant. "
                    "Summarize the supplied study material clearly. "
                    "Include key concepts, definitions, and exam points. "
                    "Do not invent facts."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Summarize this material in about {max_words} words:\n\n"
                    f"{pdf_text[:30000]}"
                ),
            },
        ],
        temperature=0.3,
        max_completion_tokens=2048,
        reasoning_effort="medium",
    )

    summary = response.choices[0].message.content

    if not summary:
        raise ValueError("Groq returned an empty summary.")

    return summary

def ask_question(pdf_text, question):
    if not pdf_text or not pdf_text.strip():
        raise ValueError("Please upload and extract a PDF first.")

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    config = dotenv_values(ENV_FILE)
    api_key = (config.get("GROQ_API_KEY") or "").strip()
    model = (config.get("GROQ_MODEL") or "openai/gpt-oss-120b").strip()

    if not api_key:
        raise ValueError("Groq API key is missing from .env.")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are AI StudyMate, an academic assistant. "
                    "Answer using the provided PDF material. "
                    "If the answer is not present in the material, "
                    "say so clearly instead of inventing an answer. "
                    "Explain concepts in simple, student-friendly language."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"PDF STUDY MATERIAL:\n{pdf_text[:25000]}\n\n"
                    f"STUDENT QUESTION:\n{question}"
                ),
            },
        ],
        temperature=0.3,
        max_completion_tokens=2048,
        reasoning_effort="medium",
    )

    answer = response.choices[0].message.content

    if not answer:
        raise ValueError("The AI returned an empty answer.")

    return answer



def generate_smart_notes(pdf_text, note_style="Detailed Notes"):
    """
    Generate study notes in a format based on the selected note style.
    """
    if not pdf_text or not pdf_text.strip():
        raise ValueError("PDF text is empty. Please upload a readable PDF.")

    config = dotenv_values(ENV_FILE)
    model = (
        config.get("GROQ_MODEL") or "openai/gpt-oss-120b"
    ).strip()

    client = get_groq_client()

    style_instructions = {
        "Detailed Notes": """
Create comprehensive, easy-to-understand study notes.

FORMAT REQUIREMENTS:
1. Use clear Markdown headings and subheadings for every topic.
2. Explain each concept in detailed paragraphs. Explain what it is,
   how it works, and why it is important.
3. After each explanation, include relevant bullet points for key
   characteristics, steps, types, advantages, disadvantages, and
   applications wherever applicable.
4. Include definitions, examples, and comparisons where relevant.
5. Explain technical terms in simple language.
6. Use numbered steps for processes and algorithms.
7. Use tables ONLY when comparing two or more concepts. Do not put
   the entire notes in a table.
8. Cover all important topics present in the supplied material.
9. Do not oversimplify or omit important details.
10. Use a balanced combination of explanatory paragraphs and bullet
    points. The main content must be in paragraphs and points.
""",

        "Quick Revision": """
Create concise, exam-focused quick revision notes.

FORMAT REQUIREMENTS:
1. Use Markdown tables as the PRIMARY format.
2. Organize information into tables with columns such as:
   Topic | Definition | Key Points | Example.
3. Use short bullet points inside table cells where appropriate.
4. Include important definitions, formulas, differences, keywords,
   and facts.
5. Add a short list of must-remember points after the tables.
6. Keep explanations brief and easy to revise quickly.
7. Avoid long explanatory paragraphs.
8. Cover the important topics from the supplied material.
""",

        "Exam Preparation": """
Create detailed, exam-oriented study notes.

FORMAT REQUIREMENTS:
1. Organize notes using topic headings and subheadings.
2. Explain concepts in paragraphs before listing key points.
3. Include definitions, working, types, features, and examples.
4. Add advantages, disadvantages, applications, and comparisons
   wherever relevant.
5. Use numbered steps for processes.
6. Highlight important exam terminology using bold Markdown.
7. Include possible short-answer and long-answer questions at the end.
8. Use tables only for comparisons, not for all the notes.
9. Do not claim that any question is guaranteed to appear in an exam.
"""
    }

    if note_style not in style_instructions:
        note_style = "Detailed Notes"

    prompt = f"""
Create {note_style} using ONLY the study material provided below.

Follow these formatting instructions carefully:
{style_instructions[note_style]}

Important rules:
- Preserve the technical accuracy of the source material.
- Do not invent facts, formulas, examples, or page references.
- If a detail is missing from the material, do not fabricate it.
- Use readable Markdown formatting.
- Make the notes useful for a university student preparing for exams.

STUDY MATERIAL:
{pdf_text[:25000]}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert academic tutor who creates accurate, "
                    "well-organized study notes. Follow the requested output "
                    "format strictly."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_completion_tokens=4096,
        temperature=0.3,
        reasoning_effort="medium",
    )

    notes = response.choices[0].message.content

    if not notes or not notes.strip():
        raise ValueError("The AI returned empty notes. Please try again.")

    return notes



def generate_important_lines(pdf_text, number_of_lines=15):
    if not pdf_text or not pdf_text.strip():
        raise ValueError("Please upload and extract a PDF first.")

    client = get_groq_client()

    config = dotenv_values(ENV_FILE)
    model = (
        config.get("GROQ_MODEL") or "openai/gpt-oss-120b"
    ).strip()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are AI StudyMate, an academic study assistant. "
                    "Identify the most useful and important lines from "
                    "the supplied study material. Prioritize definitions, "
                    "core concepts, formulas, technical terms, important "
                    "facts, and exam-relevant statements. Stay faithful "
                    "to the source and do not invent information. "
                    "Organize the result under clear headings. "
                    "For each item, explain briefly why it matters. "
                    "Clearly distinguish formulas from definitions. "
                    "Do not guarantee that any item will appear in an exam. "
                    "Return readable Markdown."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Find the {number_of_lines} most important lines "
                    "or key points from this study material.\n\n"
                    "Group them into suitable categories such as "
                    "Definitions, Key Concepts, Formulas, and Important "
                    "Facts. Include only categories relevant to the PDF. "
                    "Keep the selected lines concise and useful for revision. "
                    "If the material contains fewer important items, "
                    "return only the relevant items.\n\n"
                    f"STUDY MATERIAL:\n{pdf_text[:25000]}"
                ),
            },
        ],
        temperature=0.2,
        max_completion_tokens=3000,
        reasoning_effort="medium",
    )

    result = response.choices[0].message.content

    if not result or not result.strip():
        raise ValueError("The AI returned no important lines.")

    return result

