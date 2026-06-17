import faiss
import numpy as np


def create_faiss_index(embeddings):
    """
    Create a FAISS index from embeddings.
    """

    embeddings = np.array(
        embeddings,
        dtype=np.float32
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index
def search_index(
    index,
    query_embedding,
    k=3):
    """
    Retrieve top-k similar chunks.
    """

    query_embedding = np.array(
        query_embedding,
        dtype=np.float32
    )

    distances, indices = index.search(
        query_embedding,
        k
    )

    return distances, indices
def retrieve_chunks(
    query,
    chunks,
    model,
    index,
    k=3
):
    """
    Retrieve top-k chunks for a query.
    """

    query_embedding = model.encode([query])

    distances, indices = index.search(
        query_embedding.astype("float32"),
        k
    )

    results = []

    for idx in indices[0]:
        results.append(chunks[idx])

    return results