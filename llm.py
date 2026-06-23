from groq import Groq
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import os

load_dotenv()

print("GROQ KEY FOUND:", os.getenv("GROQ_API_KEY") is not None)


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_answer(context, question):

    prompt = f"""
You are an educational assistant.

Use ONLY the provided context to answer.

Context:
{context}

Question:
{question}

Answer:
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
        max_tokens=500
    )

    return response.choices[0].message.content
