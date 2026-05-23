
from sentence_transformers import SentenceTransformer
import chromadb
import uuid

# Load model once globally
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def create_vectorstore(chunks):
    print("🧠 Creating embeddings...")
    
    # Create ChromaDB client
    client = chromadb.Client()
    
    # Delete old collection if exists
    try:
        client.delete_collection("pdf_docs")
    except:
        pass
    
    collection = client.create_collection("pdf_docs")
    
    # Embed all chunks
    embeddings = MODEL.encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]
    
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )
    
    print(f"✅ {len(chunks)} chunks stored in vector DB!")
    return collection

def retrieve(collection, query, top_k=4):
    query_embedding = MODEL.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    return results["documents"][0]  # list of top chunks
