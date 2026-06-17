from sentence_transformers import SentenceTransformer

# Load model only once
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts):
    """
    Generate embeddings for a list of texts.

    Parameters:
        texts (list): List of sentences/chunks

    Returns:
        embeddings (numpy array)
    """

    embeddings = model.encode(texts)

    return embeddings