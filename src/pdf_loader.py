import fitz  

def load_and_split(pdf_path, chunk_size=500, overlap=50):
    print(f"📄 Loading: {pdf_path}")
    doc = fitz.open(pdf_path)
    

    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    print(f"   → {len(doc)} pages, {len(full_text)} characters")
    

    chunks = []
    start = 0
    while start < len(full_text):
        end = start + chunk_size
        chunk = full_text[start:end]
        if chunk.strip(): 
            chunks.append(chunk)
        start = end - overlap 
    
    print(f"   → {len(chunks)} chunks created ✅")
    return chunks
