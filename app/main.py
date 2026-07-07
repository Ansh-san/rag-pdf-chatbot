import streamlit as st
import uuid

from src.pdf_loader import load_and_split
from src.embedder import create_vectorstore, retrieve
from src.llm_chain import ask

# ── Page Config ──────────────────────────────
st.set_page_config(
    page_title="📄 RAG PDF Chatbot",
    page_icon="📄",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 10px; padding: 10px; }
    .title { text-align: center; color: #00d4ff; }
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────
st.markdown("<h1 class='title'>📄 RAG PDF Chatbot</h1>",
            unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Upload any PDF and chat with it!</p>",
            unsafe_allow_html=True)
st.divider()

# ── Session State ─────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "collection" not in st.session_state:
    st.session_state.collection = None
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False
if "session_id" not in st.session_state:
    # Unique per browser session so concurrent users never share/overwrite
    # each other's ChromaDB collection.
    st.session_state.session_id = str(uuid.uuid4())

collection_name = f"pdf_docs_{st.session_state.session_id}"

# ── Sidebar ───────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/pdf.png", width=80)
    st.header("📁 Upload Your PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf"
    )

    if uploaded_file:
        if st.button("🚀 Process PDF", use_container_width=True):
            # Save uploaded file
            pdf_path = f"/tmp/{uploaded_file.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.read())

            try:
                with st.spinner("📖 Reading PDF..."):
                    chunks = load_and_split(pdf_path)

                with st.spinner("🧠 Creating embeddings..."):
                    st.session_state.collection = create_vectorstore(
                        chunks, collection_name=collection_name
                    )

                st.session_state.pdf_ready = True
                st.session_state.messages = []
                st.success(f"✅ Ready! {len(chunks)} chunks indexed.")
                st.info(f"📄 {uploaded_file.name}")

            except ValueError as e:
                # Raised by create_vectorstore when no text could be extracted
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ Something went wrong while processing this PDF: {e}")

    st.divider()
    st.markdown("### 🛠️ Tech Stack")
    st.markdown("- 🤖 **LLM**: Llama 3.1 via Groq")
    st.markdown("- 📦 **Vector DB**: ChromaDB")
    st.markdown("- 🧠 **Embeddings**: MiniLM-L6")
    st.markdown("- 🎨 **UI**: Streamlit")
    st.divider()
    st.markdown("Built by **Piyush Chaudhary** 👨‍💻")
    st.markdown("CSE-AI | BTech 4th Year")

# ── Chat Area ─────────────────────────────────
if not st.session_state.pdf_ready:
    st.info("👈 Upload a PDF from the sidebar to get started!")

    # Show example questions
    st.markdown("### 💡 What can you ask?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("📝 Summarize the document")
    with col2:
        st.success("❓ Ask specific questions")
    with col3:
        st.success("🔍 Find key concepts")

else:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask anything about your PDF..."):

        # Show user message
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )
        with st.chat_message("user"):
            st.write(prompt)

        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                top_chunks = retrieve(
                    st.session_state.collection, prompt
                )
                answer = ask(prompt, top_chunks)

            st.write(answer)

            # Show source chunks
            if top_chunks:
                with st.expander("📚 View Source Chunks Used"):
                    for i, chunk in enumerate(top_chunks):
                        st.markdown(f"**Chunk {i+1}:**")
                        st.caption(chunk[:300] + "...")
                        st.divider()

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
