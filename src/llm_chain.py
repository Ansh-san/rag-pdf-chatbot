
from groq import Groq
import os

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def ask(question, context_chunks):
    context = "\n\n".join(context_chunks)
    
    prompt = f"""You are a helpful study assistant.
Answer ONLY using the context below.
If the answer is not found, say "Not found in document."

Context:
{context}

Question: {question}
Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # ✅ Updated model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    
    return response.choices[0].message.content
