
from pathlib import Path
from dotenv import dotenv_values
from groq import Groq
import json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


def generate_quiz(pdf_text, number_of_questions=5):
    if not pdf_text or not pdf_text.strip():
        raise ValueError("PDF text is empty.")

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
                    "You are an exam quiz generator. Create questions only "
                    "from the supplied study material. Return valid JSON only "
                    "with this structure: "
                    '{"questions":[{"question":"...","options":{"A":"...","B":"...","C":"...","D":"..."},"answer":"A","explanation":"..."}]}'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Create exactly {number_of_questions} multiple-choice "
                    f"questions from this material:\n\n{pdf_text[:25000]}"
                ),
            },
        ],
        temperature=0.2,
        max_completion_tokens=3000,
        reasoning_effort="medium",
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("The AI returned an empty quiz.")

    try:
        quiz = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The AI returned an invalid quiz format. Please try again."
        ) from error

    questions = quiz.get("questions", [])

    if not questions:
        raise ValueError("No questions were generated.")

    return questions
