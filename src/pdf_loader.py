
import fitz  # PyMuPDF

def load_and_split(pdf_path, chunk_size=500, overlap=50):
    print(f"📄 Loading: {pdf_path}")
    doc = fitz.open(pdf_path)
    
    # Extract all text page by page
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    print(f"   → {len(doc)} pages, {len(full_text)} characters")
    
    # Split into chunks manually
    chunks = []
    start = 0
    while start < len(full_text):
        end = start + chunk_size
        chunk = full_text[start:end]
        if chunk.strip():  # skip empty chunks
            chunks.append(chunk)
        start = end - overlap  # overlap between chunks
    
    print(f"   → {len(chunks)} chunks created ✅")
    return chunks
