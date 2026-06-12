import streamlit as st
from pdf_processing import extract_text_from_pdf
from chunking import paragraph_chunk_text

st.set_page_config(page_title="EduCast AI")

st.title("🎧 EduCast AI")
st.subheader("PDF Text Extraction")

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success("PDF uploaded successfully!")

    text = extract_text_from_pdf(uploaded_file)

    chunks = paragraph_chunk_text(text)
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