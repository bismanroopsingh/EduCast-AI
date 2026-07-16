from multiprocessing import context

from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_answer(context, question,history):

    prompt = f"""
You are EduCast AI, an expert educational tutor.

IMPORTANT RULES:
- Use ONLY the provided context.
- Do not invent information.
- If the answer is not in the context, say so.
- Explain concepts in simple student-friendly language.

Provide your answer in exactly this format:

📘 Simple Explanation
(Explain the concept clearly)

🌍 Real-World Example
(Give a practical example)

🔑 Key Takeaways
- Point 1
- Point 2
- Point 3

📝 Quick Quiz
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
def generate_lesson(topic, context,history,weak_topics):

    prompt = f"""
    You are EduCast AI, an intelligent personal tutor.

    The student has previously struggled with these topics:

    {weak_topics}

    Conversation history:

    {history}

    Today's lesson:

    {topic}

    Use ONLY the provided context.

    Instructions:

    - If today's topic relates to previous weak topics, briefly revise them first.
    - Explain concepts in simple student-friendly language.
    - Connect today's lesson to previous lessons whenever possible.
    - Give practical examples.
    - End with a quick recap.

    Return the lesson in this format:

    📘 Lesson Explanation

    🌍 Real-World Example

    🔑 Key Takeaways
    - Point 1
    - Point 2
    - Point 3

    📝 Mini Quiz
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
