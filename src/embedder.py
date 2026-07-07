from sentence_transformers import SentenceTransformer
import chromadb
import uuid

# Load model once globally
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# One shared in-memory client is fine; collections are now scoped per-session
# via the collection_name argument so concurrent users don't overwrite each other.
_CLIENT = chromadb.Client()


def create_vectorstore(chunks, collection_name="pdf_docs"):
    if not chunks:
        raise ValueError(
            "No text could be extracted from this PDF. It may be scanned/image-based "
            "and would need OCR before it can be indexed."
        )

    print("🧠 Creating embeddings...")

    # Delete old collection with this name if it exists (fresh start per upload)
    try:
        _CLIENT.delete_collection(collection_name)
    except Exception:
        pass

    collection = _CLIENT.create_collection(collection_name)

    embeddings = MODEL.encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
    )

    print(f"✅ {len(chunks)} chunks stored in vector DB!")
    return collection


def retrieve(collection, query, top_k=4):
    if collection is None:
        return []

    query_embedding = MODEL.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )
    return results["documents"][0]  # list of top chunks
