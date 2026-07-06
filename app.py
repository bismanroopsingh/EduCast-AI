import streamlit as st

from pdf_processing import extract_text_from_pdf
from chunking import semantic_chunk_text

from embeddings import generate_embeddings
from embeddings import model

from vector_store import (
    create_faiss_index,
    retrieve_chunks
)

from llm import (
    generate_answer,
    generate_topics,
    generate_lesson
)

from tts import text_to_audio
from quiz import generate_quiz
from database import (
    create_user,
    save_document,
    save_lesson,
    save_quiz_attempt,
    save_weak_topic
)


# ====================================
# Page Config
# ====================================

st.set_page_config(
    page_title="EduCast AI",
    layout="wide"
)

st.title("🎓 EduCast AI")
st.subheader("Conversational Audiobook Tutor")

# =====================================
# Student Login
# =====================================

st.sidebar.title("Student")

username = st.sidebar.text_input(
    "Enter your name"
)

if st.sidebar.button("Start Learning"):

    if username.strip() == "":
        st.sidebar.error("Please enter your name.")

    else:

        user_id = create_user(username)

        st.session_state["user_id"] = user_id
        st.session_state["username"] = username

        st.sidebar.success(
            f"Welcome {username}!"
        )

def parse_quiz(quiz_text):

    questions = []

    lines = quiz_text.split("\n")

    for line in lines:

        if "|" not in line:
            continue

        parts = line.split("|")

        if len(parts) != 6:
            continue

        questions.append({
            "question": parts[0].strip(),
            "options": [
                parts[1],
                parts[2],
                parts[3],
                parts[4]
            ],
            "answer": parts[5]
        })

    return questions


# ====================================
# Cache Topic Generation
# ====================================

@st.cache_data
def cached_topics(text):
    return generate_topics(text)


# ====================================
# PDF Upload
# ====================================

if "user_id" not in st.session_state:

    st.info("Enter your name in the sidebar to begin learning.")

    st.stop()

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success("PDF uploaded successfully!")

    # ====================================
    # Extract PDF Text
    # ====================================

    text = extract_text_from_pdf(
        uploaded_file
    )
    document_id = save_document(
            st.session_state["user_id"],
            uploaded_file.name,
            text
        )

    st.session_state["document_id"] = document_id

    # ====================================
    # Semantic Chunking
    # ====================================

    chunks = semantic_chunk_text(text)

    st.success(
        f"Created {len(chunks)} chunks"
    )

    # ====================================
    # Embeddings
    # ====================================

    chunk_embeddings = generate_embeddings(
        chunks
    )

    # ====================================
    # FAISS Index
    # ====================================

    index = create_faiss_index(
        chunk_embeddings
    )

    # ====================================
    # Generate Topics
    # ====================================

    if "topics" not in st.session_state:

        st.session_state["topics"] = cached_topics(
            text
        )

    topics = st.session_state["topics"]

    topic_list = []

    for topic in topics.split("\n"):

        topic = topic.strip()

        if topic:
            topic_list.append(topic)

    st.subheader("Generated Lessons")

    selected_topic = st.selectbox(
        "Choose a Lesson",
        topic_list
    )

    # ====================================
    # Generate Lesson
    # ====================================

    if st.button("Generate Lesson"):

        lesson_results = retrieve_chunks(
            selected_topic,
            chunks,
            model,
            index,
            k=8
        )

        lesson_context = "\n\n".join(
            lesson_results
        )

        lesson = generate_lesson(
            selected_topic,
            lesson_context
        )
        lesson_id = save_lesson(
            st.session_state["document_id"],
            selected_topic,
            lesson
        )

        st.session_state["lesson_id"] = lesson_id
        st.session_state["lesson"] = lesson
        st.session_state["lesson_topic"] = selected_topic

        st.subheader(
            "📚 Generated Lesson"
        )

        st.write(lesson)

        audio_file = text_to_audio(
            lesson
        )

        st.subheader(
            "Lesson Audio"
        )

        st.audio(
            audio_file,
            format="audio/mp3"
        )

        with st.expander(
            "Lesson Context"
        ):

            for i, result in enumerate(
                lesson_results
            ):

                st.write(
                    f"### Chunk {i+1}"
                )

                st.write(result)

    # ====================================
    # Show Existing Lesson
    # ====================================

    if ("lesson" in st.session_state
    and
    "lesson_topic" in st.session_state):

        st.subheader(
            "Current Lesson"
        )

        st.write(
            st.session_state["lesson"]
        )

        # ================================
        # Quiz Generation
        # ================================

        if st.button(
            "Generate Quiz"
        ):

            quiz = generate_quiz(
                st.session_state[
                    "lesson_topic"
                ],
                st.session_state[
                    "lesson"
                ]
            )

            st.session_state["quiz"] = quiz

        if "quiz" in st.session_state:

            st.subheader("Quiz")

            quiz_data = parse_quiz(
                st.session_state["quiz"]
            )
            st.write("Raw Quiz Output:")
            st.code(st.session_state["quiz"])

            st.write("Parsed Quiz:")
            st.write(quiz_data)
            user_answers = []

            # -----------------------------
            # Display Questions
            # -----------------------------
            for i, q in enumerate(quiz_data):

                answer = st.radio(
                    q["question"],
                    q["options"],
                    key=f"q{i}"
                )

                user_answers.append(answer)

            # -----------------------------
            # Submit Button
            # -----------------------------
            if st.button("Submit Quiz"):

                score = 0

                letter_map = {
                    "A":0,
                    "B":1,
                    "C":2,
                    "D":3
                }

                for i, q in enumerate(quiz_data):

                    correct_letter = q["answer"].strip().upper()

                    correct_option = q["options"][
                        letter_map[correct_letter]
                    ]

                    if user_answers[i] == correct_option:
                        score += 1

                st.success(
                    f"Score: {score}/{len(quiz_data)}"
                )

                percentage = (score / len(quiz_data)) * 100

                save_quiz_attempt(
                    st.session_state["user_id"],
                    st.session_state["lesson_id"],
                    score,
                    len(quiz_data),
                    percentage
                )

                if percentage < 70:
                    save_weak_topic(
                        st.session_state["user_id"],
                        st.session_state["lesson_id"],
                        st.session_state["lesson_topic"],
                        100 - percentage
                    )

                st.write(
                    f"Percentage: {percentage:.2f}%"
                )


        # ====================================
    # Question Answering
    # ====================================

    st.subheader(
        "Ask a Question"
    )

    question = st.text_input(
        "Ask a question about the PDF"
    )

    if question:

        results = retrieve_chunks(
            question,
            chunks,
            model,
            index,
            k=3
        )

        context = "\n\n".join(
            results
        )

        answer = generate_answer(
            context,
            question
        )

        st.subheader(
            "AI Answer"
        )

        st.write(answer)

        audio_file = text_to_audio(
            answer
        )

        st.subheader(
            "🎧 Audio Answer"
        )

        st.audio(
            audio_file,
            format="audio/mp3"
        )

        with st.expander(
            "Retrieved Context"
        ):

            for i, result in enumerate(
                results
            ):

                st.write(
                    f"### Result {i+1}"
                )

                st.write(result)

    # ====================================
    # View Chunks
    # ====================================

    st.subheader(
        "Generated Chunks"
    )

    for i, chunk in enumerate(
        chunks
    ):

        with st.expander(
            f"Chunk {i+1}"
        ):

            st.write(chunk)

    # ====================================
    # Full PDF Text
    # ====================================

    st.subheader(
        "PDF Content"
    )

    st.text_area(
        "Extracted Text",
        text,
        height=400
    )

