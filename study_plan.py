from llm import client


def generate_study_plan(
    username,
    weak_topics,
    quiz_history,
    lessons
):

    # -----------------------------
    # Format quiz history
    # -----------------------------

    if len(quiz_history) == 0:
        quiz_text = "No quizzes attempted yet."

    else:

        quiz_text = ""

        for q in quiz_history:

            quiz_text += (
                f"Score: {q['score']}/"
                f"{q['total_questions']}, "
                f"Percentage: {q['percentage']}%\n"
            )

    # -----------------------------
    # Format weak topics
    # -----------------------------

    if len(weak_topics) == 0:

        weak_text = "No weak topics detected."

    else:

        weak_text = ""

        for topic in weak_topics:

            weak_text += (
                f"- {topic['topic']} "
                f"(Weakness Score: {topic['weakness_score']})\n"
            )

    # -----------------------------
    # Format lessons
    # -----------------------------

    if len(lessons) == 0:

        lesson_text = "No lessons generated."

    else:

        lesson_text = ""

        for lesson in lessons:

            lesson_text += f"- {lesson['topic']}\n"

    # -----------------------------
    # Prompt
    # -----------------------------

    prompt = f"""
You are an expert AI tutor.

Student Name:
{username}

Quiz History:

{quiz_text}

Weak Topics:

{weak_text}

Lessons Studied:

{lesson_text}

Generate a personalized 7-day study plan.

Requirements:

- Day-wise schedule
- Morning session
- Afternoon session
- Evening revision
- Estimated study time
- Mention which weak topics should be revised
- Mention when quizzes should be retaken
- Encourage spaced repetition

Keep it practical and motivating.
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