from groq import Groq
import os
from dotenv import load_dotenv

# Load variables from a local .env file if present (safe no-op if it doesn't exist)
load_dotenv()

_API_KEY = os.environ.get("GROQ_API_KEY")

if not _API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Create a .env file in the project root "
        "with a line like:\n\nGROQ_API_KEY=your_key_here\n\n"
        "or export it in your shell before running the app."
    )

client = Groq(api_key=_API_KEY)


def ask(question, context_chunks):
    if not context_chunks:
        return "Not found in document."

    context = "\n\n".join(context_chunks)

    prompt = f"""You are a helpful study assistant.
Answer ONLY using the context below.
If the answer is not found, say "Not found in document."

Context:
{context}

Question: {question}
Answer:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:

        return f"⚠️ Error contacting Groq API: {e}"
