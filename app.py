import streamlit as st
from pdf_processing import extract_text_from_pdf
from chunking import semantic_chunk_text
from embeddings import generate_embeddings
from vector_store import create_faiss_index
from embeddings import model
from vector_store import retrieve_chunks
from llm import generate_answer
from tts import text_to_audio

st.set_page_config(page_title="EduCast AI")

st.title("EduCast AI")
st.subheader("PDF Text Extraction")

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success("PDF uploaded successfully!")
    
    text = extract_text_from_pdf(uploaded_file)

    chunks = semantic_chunk_text(text)

    chunk_embeddings = generate_embeddings(chunks)

    index = create_faiss_index(chunk_embeddings)
    question = st.text_input(
        "Ask a question about the PDF"
    )

    if question:

        st.subheader("Retrieved Context")

        results = retrieve_chunks(
            question,
            chunks,
            model,
            index,
            k=3
        )
        context = "\n\n".join(results)
        answer = generate_answer(
        context,
        question
    )
        st.subheader("AI Answer")
        st.write(answer)
        # Optional: Show retrieved chunks
        st.subheader("Retrieved Context")
        audio_file = text_to_audio(answer)
        st.subheader("Audio Lesson")
        st.audio(audio_file, format="audio/mp3")
        
        for i, result in enumerate(results):
            st.write(f"### Result {i+1}")
            st.write(result)

    st.success(f"Created {len(chunks)} chunks")

    st.subheader("Extracted Text")

    for i, chunk in enumerate(chunks):
        with st.expander(f"Chunk {i+1}"):
            st.write(chunk)

    st.text_area(
        "PDF Content",
        text,
        height=400
    )
