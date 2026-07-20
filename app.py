import streamlit as st
from flashcards import generate_flashcards
from pdf_processing import extract_text_from_pdf
from chunking import semantic_chunk_text

from embeddings import generate_embeddings
from embeddings import model
from study_plan import generate_study_plan
from vector_store import (
    create_faiss_index,
    retrieve_chunks
)
import pandas as pd
import plotly.express as px
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
    save_weak_topic,
    get_documents,
    get_quiz_history,
    get_document_count,
    get_lesson_count,
    get_quiz_count,
    get_average_score,
    get_weak_topic_count,
    get_weak_topics,
    get_dashboard_stats,
    get_quiz_scores,
    get_top_weak_topics,
    get_recent_documents,
    get_recommended_topics,
    get_documents,
    get_lessons,
    get_user_progress,
    get_weak_topics,
    get_all_lessons
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


def parse_flashcards(text):
    cards = []

    for line in text.split("\n"):
        if "|" not in line:
            continue

        q, a = line.split("|", 1)

        cards.append({
            "question": q.strip(),
            "answer": a.strip()
        })

    return cards


# ====================================
# Cache Topic Generation
# ====================================

@st.cache_data
def cached_topics(text):
    return generate_topics(text)


# ------------------------------------------------------------
# FIX: cache flashcard/quiz generation keyed on the exact lesson
# text + topic. If the same lesson is used again (e.g. after a
# page rerun triggered by an unrelated button), Streamlit returns
# the cached result instantly instead of calling Groq again.
# ------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_generate_flashcards(topic, lesson_text):
    return generate_flashcards(topic, lesson_text)


@st.cache_data(show_spinner=False)
def cached_generate_quiz(topic, lesson_text):
    return generate_quiz(topic, lesson_text)


# ------------------------------------------------------------
# FIX: cache read-only dashboard/progress DB queries for a short
# window so switching pages back and forth doesn't re-hit MySQL
# every single time. Adjust ttl as needed.
# ------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def cached_dashboard_stats(user_id):
    return get_dashboard_stats(user_id)


@st.cache_data(ttl=30, show_spinner=False)
def cached_quiz_scores(user_id):
    return get_quiz_scores(user_id)


@st.cache_data(ttl=30, show_spinner=False)
def cached_top_weak_topics(user_id):
    return get_top_weak_topics(user_id)


@st.cache_data(ttl=30, show_spinner=False)
def cached_recent_documents(user_id):
    return get_recent_documents(user_id)


@st.cache_data(ttl=30, show_spinner=False)
def cached_recommended_topics(user_id):
    return get_recommended_topics(user_id)


@st.cache_data(ttl=30, show_spinner=False)
def cached_user_progress(user_id):
    return get_user_progress(user_id)


# =====================================
# Student Login
# =====================================

st.sidebar.title("👤 Student")

username = st.sidebar.text_input("Enter your name")

if st.sidebar.button("Start Learning"):
    if username.strip() == "":
        st.sidebar.error("Please enter your name.")
    else:
        user_id = create_user(username)
        st.session_state["user_id"] = user_id
        st.session_state["username"] = username
        st.sidebar.success(f"Welcome {username}!")

if "user_id" not in st.session_state:
    st.info("Enter your name in the sidebar to begin learning.")
    st.stop()

st.sidebar.markdown("---")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

page = st.sidebar.radio(
    "📚 Navigation",
    [
        "Learn",
        "Study Plan",
        "Dashboard",
        "Documents",
        "Progress"
    ]
)

# ====================================
# PDF Upload / Learn Page
# ====================================

if page == "Learn":

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    # ------------------------------------------------------------
    # FIX: support MULTIPLE files. Each processed file is stored
    # under its own fingerprint key inside "library", instead of
    # overwriting a single set of session_state variables.
    # ------------------------------------------------------------
    if "library" not in st.session_state:
        st.session_state["library"] = {}   # fingerprint -> {name, text, chunks, index, topics, document_id}

    if uploaded_file is not None:
        file_fingerprint = f"{uploaded_file.name}_{uploaded_file.size}"

        if file_fingerprint not in st.session_state["library"]:

            text = extract_text_from_pdf(uploaded_file)
            document_id = save_document(
                st.session_state["user_id"],
                uploaded_file.name,
                text
            )

            chunks = semantic_chunk_text(text)
            chunk_embeddings = generate_embeddings(chunks)
            index = create_faiss_index(chunk_embeddings)
            topics = cached_topics(text)

            st.session_state["library"][file_fingerprint] = {
                "name": uploaded_file.name,
                "text": text,
                "chunks": chunks,
                "index": index,
                "topics": topics,
                "document_id": document_id,
            }

            # Make the newly uploaded file the active one
            st.session_state["active_fingerprint"] = file_fingerprint

            st.success(f"Added new file: {uploaded_file.name}")
        else:
            st.info(f"'{uploaded_file.name}' is already in your library.")

    # ------------------------------------------------------------
    # Pick which uploaded file is active. Switching this dropdown
    # is what changes the lesson/quiz/chat context - not re-uploading.
    # ------------------------------------------------------------
    if len(st.session_state["library"]) > 0:

        fingerprint_to_label = {
            fp: doc["name"] for fp, doc in st.session_state["library"].items()
        }

        options = list(fingerprint_to_label.keys())
        default_index = (
            options.index(st.session_state["active_fingerprint"])
            if st.session_state.get("active_fingerprint") in options
            else 0
        )

        selected_fingerprint = st.selectbox(
            "📂 Active document",
            options,
            index=default_index,
            format_func=lambda fp: fingerprint_to_label[fp]
        )

        # If the user switched documents, reset lesson/quiz/chat state
        if st.session_state.get("active_fingerprint") != selected_fingerprint:
            st.session_state["active_fingerprint"] = selected_fingerprint
            for key in ["lesson", "lesson_topic", "lesson_id", "flashcards", "quiz", "lesson_results"]:
                st.session_state.pop(key, None)
            st.session_state["chat_history"] = []

    # ------------------------------------------------------------
    # Load the active document's data from the library into the
    # variables the rest of the page already uses.
    # ------------------------------------------------------------
    if st.session_state.get("active_fingerprint") in st.session_state.get("library", {}):

        active_doc = st.session_state["library"][st.session_state["active_fingerprint"]]

        text = active_doc["text"]
        chunks = active_doc["chunks"]
        index = active_doc["index"]
        topics = active_doc["topics"]
        st.session_state["document_id"] = active_doc["document_id"]

        topic_list = []
        for topic in topics.split("\n"):
            topic = topic.strip()
            if topic:
                topic_list.append(topic)

        st.subheader("📚 Generated Lessons")

        selected_topic = st.selectbox("Choose a Lesson", topic_list)

        # ====================================
        # Generate Lesson
        # ====================================

        if st.button("📖 Generate Lesson"):

            with st.spinner("Retrieving relevant content..."):
                lesson_results = retrieve_chunks(
                    selected_topic,
                    chunks,
                    model,
                    index,
                    k=5
                )

            lesson_context = "\n\n".join(lesson_results)
            history = st.session_state.get("chat_history", [])

            weak_topics = get_weak_topics(st.session_state["user_id"])

            with st.spinner("Generating your lesson with AI..."):
                lesson = generate_lesson(
                    selected_topic,
                    lesson_context,
                    history,
                    weak_topics
                )
            lesson_id = save_lesson(
                st.session_state["document_id"],
                selected_topic,
                lesson
            )

            st.session_state["lesson_id"] = lesson_id
            st.session_state["lesson"] = lesson
            st.session_state["lesson_topic"] = selected_topic
            st.session_state["lesson_results"] = lesson_results

            # New lesson means old flashcards/quiz/audio no longer apply
            st.session_state.pop("flashcards", None)
            st.session_state.pop("quiz", None)
            st.session_state.pop("lesson_audio", None)

        # ====================================
        # Show Existing Lesson
        # ====================================
        if "lesson" in st.session_state and "lesson_topic" in st.session_state:

            st.subheader("📚 Current Lesson")
            st.write(st.session_state["lesson"])

            # FIX: audio is now generated ONLY on demand, not automatically
            # on every lesson render. This removes gTTS from the critical
            # path of lesson generation entirely.
            if st.button("🔊 Generate Lesson Audio"):
                with st.spinner("Converting lesson to audio..."):
                    st.session_state["lesson_audio"] = text_to_audio(st.session_state["lesson"])

            if "lesson_audio" in st.session_state:
                st.subheader("🎧 Lesson Audio")
                st.audio(st.session_state["lesson_audio"], format="audio/mp3")

            if "lesson_results" in st.session_state:
                with st.expander("📄 Lesson Context"):
                    for i, result in enumerate(st.session_state["lesson_results"]):
                        st.write(f"### Chunk {i+1}")
                        st.write(result)

            # -------------------------
            # Flashcards
            # -------------------------

            if st.button("🃏 Generate Flashcards"):
                with st.spinner("Generating flashcards with AI..."):
                    flashcards = cached_generate_flashcards(
                        st.session_state["lesson_topic"],
                        st.session_state["lesson"]
                    )
                st.session_state["flashcards"] = flashcards

            if "flashcards" in st.session_state:

                cards = parse_flashcards(st.session_state["flashcards"])

                st.subheader("🃏 Flashcards")

                for i, card in enumerate(cards):
                    with st.expander(f"Flashcard {i+1}"):
                        st.write("### Question")
                        st.write(card["question"])
                        st.write("### Answer")
                        st.write(card["answer"])

            # -------------------------
            # Quiz
            # -------------------------

            if st.button("📝 Generate Quiz"):
                with st.spinner("Generating quiz with AI..."):
                    quiz = cached_generate_quiz(
                        st.session_state["lesson_topic"],
                        st.session_state["lesson"]
                    )
                st.session_state["quiz"] = quiz

            if "quiz" in st.session_state:

                st.subheader("📝 Quiz")

                quiz_data = parse_quiz(st.session_state["quiz"])

                user_answers = []

                for i, q in enumerate(quiz_data):
                    answer = st.radio(q["question"], q["options"], key=f"q{i}")
                    user_answers.append(answer)

                if st.button("Submit Quiz"):

                    score = 0
                    letter_map = {"A": 0, "B": 1, "C": 2, "D": 3}

                    for i, q in enumerate(quiz_data):
                        correct_letter = q["answer"].strip().upper()
                        correct_option = q["options"][letter_map[correct_letter]]

                        if user_answers[i] == correct_option:
                            score += 1

                    st.success(f"Score: {score}/{len(quiz_data)}")

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

                    st.write(f"Percentage: {percentage:.2f}%")

        # ====================================
        # Question Answering
        # ====================================

        st.subheader("❓ Ask a Question")

        st.subheader("💬 Conversation")

        if len(st.session_state["chat_history"]) == 0:
            st.info("Start asking questions about your PDF!")

        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])

        question = st.text_input("Ask a question about the PDF")

        # ------------------------------------------------------------
        # FIX (important): st.text_input keeps its value across every
        # rerun, including reruns triggered by OTHER buttons on the
        # page (e.g. clicking "Submit Quiz"). Without this guard, the
        # SAME question was being re-sent to Groq and re-appended to
        # chat_history on every unrelated click — this is very likely
        # why "Submit Quiz" and other buttons felt slow: a hidden
        # extra Groq call was firing in the background every time.
        # We now only process a question if it's different from the
        # last one we already answered.
        # ------------------------------------------------------------
        if question and question != st.session_state.get("last_question"):

            st.session_state["last_question"] = question

            with st.spinner("Searching document and generating answer..."):
                results = retrieve_chunks(question, chunks, model, index, k=3)
                context = "\n\n".join(results)

                answer = generate_answer(
                    context,
                    question,
                    st.session_state["chat_history"]
                )

            st.session_state["chat_history"].append(
                {"role": "user", "content": question}
            )
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": answer}
            )
            st.session_state["last_answer"] = answer
            st.session_state["last_answer_context"] = results
            st.session_state.pop("qa_audio", None)

        if "last_answer" in st.session_state:

            answer = st.session_state["last_answer"]
            results = st.session_state.get("last_answer_context", [])

            st.subheader("🤖 AI Answer")
            st.write(answer)

            # FIX: audio generated only on demand, not on every rerun
            if st.button("🔊 Generate Answer Audio"):
                with st.spinner("Converting answer to audio..."):
                    st.session_state["qa_audio"] = text_to_audio(answer)

            if "qa_audio" in st.session_state:
                st.subheader("🎧 Audio Answer")
                st.audio(st.session_state["qa_audio"], format="audio/mp3")

            with st.expander("📄 Retrieved Context"):
                for i, result in enumerate(results):
                    st.write(f"### Result {i+1}")
                    st.write(result)

        # ====================================
        # View Chunks
        # ====================================

        st.subheader("📑 Generated Chunks")

        for i, chunk in enumerate(chunks):
            with st.expander(f"Chunk {i+1}"):
                st.write(chunk)

        # ====================================
        # Full PDF Text
        # ====================================

        st.subheader("📄 PDF Content")
        st.text_area("Extracted Text", text, height=400)

    else:
        st.info("Upload a PDF above to get started.")


# ====================================
# Documents Page
# ====================================

elif page == "Documents":

    st.title("📄 My Documents")

    documents = get_documents(st.session_state["user_id"])

    if len(documents) == 0:
        st.info("No documents uploaded yet.")
    else:
        for doc in documents:
            with st.expander(f"📘 {doc['file_name']}"):

                st.write(f"**Document ID:** {doc['document_id']}")
                st.subheader("Preview")

                preview = doc["content"][:800]
                st.text(preview + "...")

                if "uploaded_at" in doc:
                    st.write(f"Uploaded: {doc['uploaded_at']}")

                lessons = get_lessons(doc["document_id"])

                if len(lessons) == 0:
                    st.warning("No lessons generated yet.")
                else:
                    st.subheader("Generated Lessons")
                    for lesson in lessons:
                        with st.expander(f"📚 {lesson['topic']}"):
                            st.write(lesson["lesson_text"])
                        st.divider()


# ====================================
# Progress Page
# ====================================

elif page == "Progress":

    st.title("📈 Learning Progress")

    stats = cached_dashboard_stats(st.session_state["user_id"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Documents", stats["documents"])
    c2.metric("📚 Lessons", stats["lessons"])
    c3.metric("📝 Quizzes", stats["quizzes"])
    c4.metric("🎯 Avg Score", f"{stats['average_score']}%")

    st.divider()

    st.subheader("📊 Quiz Performance")

    scores = cached_quiz_scores(st.session_state["user_id"])

    if len(scores) > 0:
        df = pd.DataFrame(scores)
        fig = px.line(
            df,
            x="attempt_date",
            y="percentage",
            markers=True,
            title="Quiz Scores Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No quizzes attempted yet.")

    st.divider()

    st.subheader("⚠ Weak Topics")

    weak = cached_top_weak_topics(st.session_state["user_id"])

    if len(weak) > 0:
        df = pd.DataFrame(weak)
        fig = px.bar(
            df,
            x="topic",
            y="frequency",
            color="frequency",
            title="Topics Requiring More Practice"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No weak topics recorded.")

    st.divider()

    st.subheader("📝 Recent Quiz Attempts")

    progress = cached_user_progress(st.session_state["user_id"])

    if len(progress) > 0:
        df = pd.DataFrame(progress)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No quiz history found.")

    st.divider()

    st.subheader("🤖 AI Study Recommendation")

    if len(weak) > 0:
        st.write("You should revise these topics first:")
        for topic in weak:
            st.warning(topic["topic"])
    else:
        st.success("Excellent! No weak topics detected.")


# ====================================
# Study Plan Page
# ====================================

elif page == "Study Plan":

    st.title("📅 AI Personalized Study Plan")

    if st.button("Generate Study Plan"):

        quiz_history = get_quiz_history(st.session_state["user_id"])
        weak_topics = get_weak_topics(st.session_state["user_id"])
        lessons = get_all_lessons(st.session_state["user_id"])

        plan = generate_study_plan(
            st.session_state["username"],
            weak_topics,
            quiz_history,
            lessons
        )

        st.session_state["study_plan"] = plan

    if "study_plan" in st.session_state:
        st.subheader("Your AI Study Plan")
        st.write(st.session_state["study_plan"])


# ====================================
# Dashboard Page
# ====================================

elif page == "Dashboard":

    st.title("📊 Learning Dashboard")

    stats = cached_dashboard_stats(st.session_state["user_id"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📄 Documents", stats["documents"])
    c2.metric("📚 Lessons", stats["lessons"])
    c3.metric("📝 Quizzes", stats["quizzes"])
    c4.metric("🎯 Avg Score", f'{stats["average_score"]}%')
    c5.metric("⚠ Weak Topics", stats["weak_topics"])

    st.divider()

    # quiz_scores = cached_quiz_scores(st.session_state["user_id"])

    # if len(quiz_scores) > 0:
    #     df = pd.DataFrame(quiz_scores)
    #     fig = px.line(
    #         df,
    #         x="attempt_date",
    #         y="percentage",
    #         markers=True,
    #         title="Quiz Performance"
    #     )
    #     st.plotly_chart(fig, use_container_width=True)

    # st.subheader("📉 Weak Topics")

    # weak = cached_top_weak_topics(st.session_state["user_id"])

    # if len(weak) > 0:
    #     df = pd.DataFrame(weak)
    #     fig = px.bar(
    #         df,
    #         x="topic",
    #         y="frequency",
    #         color="frequency",
    #         title="Most Difficult Topics"
    #     )
    #     st.plotly_chart(fig, use_container_width=True)

    st.subheader("📄 Recent Documents")

    docs = cached_recent_documents(st.session_state["user_id"])
    for doc in docs:
        st.write(f"📘 {doc['file_name']}")

    st.subheader("🎯 Recommended Topics")

    topics = cached_recommended_topics(st.session_state["user_id"])
    for topic in topics:
        st.success(topic["topic"])


st.markdown("---")
st.caption("EduCast AI • Built with Streamlit • Groq Llama 3.1 • FAISS • MySQL")
