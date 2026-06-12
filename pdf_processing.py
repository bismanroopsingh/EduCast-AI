import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_file):
    """
    Extracts text from an uploaded PDF file.

    Parameters:
        pdf_file: Uploaded PDF file object from Streamlit

    Returns:
        Extracted text as a string
    """

    document = fitz.open(stream=pdf_file.read(), filetype="pdf")

    extracted_text = ""

    for page in document:
        extracted_text += page.get_text()

    document.close()

    return extracted_text