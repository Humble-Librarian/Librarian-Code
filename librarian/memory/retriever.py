import os
import chromadb
from sentence_transformers import SentenceTransformer
from librarian.utils.config import CHROMA_PERSIST_DIR, EMBED_MODEL


def retrieve(query: str, n_results: int = 5) -> list[dict]:
    model = SentenceTransformer(EMBED_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    project_name = os.path.basename(os.getcwd())
    collection = client.get_collection(name=project_name)

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist > 0.8:
            continue
        chunks.append({
            "content": doc,
            "metadata": meta,
            "distance": dist,
        })
    return chunks
