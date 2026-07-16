from llm import client


def generate_flashcards(topic, lesson):

    prompt = f"""
You are an AI tutor.

Generate exactly 10 flashcards from the lesson.

Topic:
{topic}

Lesson:
{lesson}

Format EXACTLY like this:

Question|Answer

Example:

What is AI?|Artificial Intelligence enables machines to perform human-like tasks.

Do NOT use numbering.
Do NOT use bullet points.
Only output Question|Answer.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content