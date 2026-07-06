from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_answer(context, question):

    prompt = f"""
You are EduCast AI, an expert educational tutor.

IMPORTANT RULES:
- Use ONLY the provided context.
- Do not invent information.
- If the answer is not in the context, say so.
- Explain concepts in simple student-friendly language.

Provide your answer in exactly this format:

Simple Explanation
(Explain the concept clearly)

Real-World Example
(Give a practical example)

Key Takeaways
- Point 1
- Point 2
- Point 3

Quick Quiz
1. Question
2. Question

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=700
    )

    return response.choices[0].message.content
def generate_topics(text):

    prompt = f"""
You are EduCast AI.

Analyze the following academic document and identify
the main learning topics.

Rules:
- Return only the major topics.
- Create between 5 and 10 topics.
- Keep topic names short.
- Return a numbered list.

Document:

{text[:12000]}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=300
    )

    return response.choices[0].message.content
def generate_lesson(topic, context):

    prompt = f"""
You are EduCast AI.

Create a complete educational lesson on:

{topic}

Using ONLY the provided context.

Format:

Lesson Explanation
Real-World Example

Key Takeaways
- Point 1
- Point 2
- Point 3

Mini Quiz
1. Question
2. Question

Context:
{context}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=800
    )

    return response.choices[0].message.content
