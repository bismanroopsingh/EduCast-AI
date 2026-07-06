from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_quiz(topic, lesson):

    prompt = f"""
Create 5 MCQ questions.

Question|OptionA|OptionB|OptionC|OptionD|CorrectLetter

Example:

What is AI?|Artificial Intelligence|Artificial Ice|Artificial Ink|Artificial Input|A

Rules:

- Do NOT number questions.
- Do NOT write Q1.
- Do NOT write A)
- Do NOT write Correct Answer.
- Output exactly one line per question.
- The last field must ONLY be A B C or D.

Topic:
{topic}

Lesson:
{lesson}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=800
    )

    return response.choices[0].message.content
