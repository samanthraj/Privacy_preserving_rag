import os
import uuid
from typing import List, Dict

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import MarkdownTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from langchain_groq import ChatGroq

# =========================
# 🔐 LOAD ENV
# =========================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================
# 🔹 PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(BASE_DIR, "../data/pdffiles")
VECTOR_DB_PATH = os.path.join(BASE_DIR, "../data/vectorstore")

# =========================
# 🔹 EMBEDDING MODEL
# =========================
class EmbeddingModel:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]):
        return self.model.encode(texts)

embedding_manager = EmbeddingModel()

# =========================
# 🔹 LOAD DOCUMENTS
# =========================
loader = DirectoryLoader(PDF_PATH, glob="**/*.pdf", loader_cls=PyMuPDFLoader)
documents = loader.load()

# =========================
# 🔹 TEXT SPLITTING
# =========================
splitter = MarkdownTextSplitter(chunk_size=300, chunk_overlap=20)

chunks = []
for doc in documents:
    text_chunks = splitter.split_text(doc.page_content)
    for i, chunk in enumerate(text_chunks):
        chunks.append(
            Document(
                page_content=chunk,
                metadata={**doc.metadata, "chunk_index": i}
            )
        )

# =========================
# 🔹 EMBEDDINGS
# =========================
chunk_texts = [chunk.page_content for chunk in chunks]
embeddings = embedding_manager.generate_embeddings(chunk_texts)

# =========================
# 🔹 VECTOR STORE
# =========================
client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
collection = client.get_or_create_collection(name="rag_data")

if collection.count() == 0:
    collection.add(
        ids=[str(uuid.uuid4()) for _ in chunk_texts],
        embeddings=[e.tolist() for e in embeddings],
        documents=chunk_texts
    )

# =========================
# 🔹 RETRIEVER
# =========================
class RAGRetriever:
    def __init__(self, collection, embedding_manager):
        self.collection = collection
        self.embedding_manager = embedding_manager

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        return results.get("documents", [[]])[0]

ragretriever = RAGRetriever(collection, embedding_manager)

# =========================
# 🔹 LLM
# =========================
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    max_tokens=4096       # ⬆️ increased for longer responses
)

# =========================
# 💬 CONVERSATION HISTORY STORE
# Per-user history: { user_id: [ {"role": "user"|"assistant", "content": "..."}, ... ] }
# =========================
conversation_histories: Dict[str, List[Dict[str, str]]] = {}

MAX_HISTORY_TURNS = 10  # keep last 10 turns (20 messages) to avoid context overflow

def get_history(user_id: str) -> List[Dict[str, str]]:
    """Return conversation history for a given user."""
    return conversation_histories.get(str(user_id), [])

def add_to_history(user_id: str, role: str, content: str):
    """Append a message to the user's conversation history."""
    uid = str(user_id)
    if uid not in conversation_histories:
        conversation_histories[uid] = []

    conversation_histories[uid].append({"role": role, "content": content})

    # Trim to last MAX_HISTORY_TURNS turns (each turn = 1 user + 1 assistant msg)
    max_messages = MAX_HISTORY_TURNS * 2
    if len(conversation_histories[uid]) > max_messages:
        conversation_histories[uid] = conversation_histories[uid][-max_messages:]

def clear_history(user_id: str):
    """Clear conversation history for a user."""
    conversation_histories.pop(str(user_id), None)

def build_langchain_messages(history: List[Dict[str, str]], system_prompt: str):
    """Convert history list + system prompt into LangChain message objects."""
    messages = [SystemMessage(content=system_prompt)]
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    return messages

# =========================
# 🧠 AGENT DECISION (LLM)
# =========================
def needs_retrieval(query: str) -> bool:
    decision_prompt = f"""
    Decide if this question requires searching through external legal documents
    to provide an accurate and complete answer.

    Question: {query}

    Answer ONLY "YES" or "NO".
    """
    response = llm.invoke(decision_prompt).content.strip().upper()
    return "YES" in response

# =========================
# 🤖 AGENTIC RAG  (now accepts user_id for per-user history)
# =========================
def agentic_rag(query: str, user_id: str = "default"):
    try:
        history = get_history(user_id)

        # ─── PATH A: No retrieval needed ────────────────────────────────────
        if not needs_retrieval(query):
            system_prompt = (
                "You are a knowledgeable and articulate legal assistant. "
                "Answer the user's question in a thorough, well-structured manner. "
                "Use clear headings or numbered points where appropriate. "
                "Provide detailed explanations, relevant examples, and practical insights. "
                "Be comprehensive — aim for at least 3–5 paragraphs unless the question is trivial. "
                "Refer to prior conversation context when relevant."
            )

            messages = build_langchain_messages(history, system_prompt)
            messages.append(HumanMessage(content=query))

            response = llm.invoke(messages)
            answer = response.content

        # ─── PATH B: Retrieval needed ────────────────────────────────────────
        else:
            docs = ragretriever.retrieve(query)

            if not docs:
                answer = (
                    "I searched through the available legal documents but could not find "
                    "information directly relevant to your question. Please try rephrasing, "
                    "or consult a qualified legal professional for guidance."
                )
                add_to_history(user_id, "user", query)
                add_to_history(user_id, "assistant", answer)
                return answer

            context = "\n\n".join(docs)

            # Build a history-aware context summary for the system prompt
            history_text = ""
            if history:
                history_text = (
                    "\n\nConversation so far (use this for context and continuity):\n"
                    + "\n".join(
                        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                        for m in history[-6:]   # last 3 turns inline in prompt
                    )
                )

            system_prompt = (
                "You are a highly experienced legal assistant with deep expertise in legal "
                "document analysis and interpretation. "
                "Your responses must be thorough, well-structured, and professionally written. "
                "Use the provided document context as your primary source of truth. "
                "If the answer is not found in the context, clearly state: "
                "'I don't know based on the provided documents.' "
                "Structure your answer with clear sections, bullet points, or numbered lists "
                "where appropriate. Provide explanations, implications, and practical takeaways. "
                "Aim for comprehensive answers — typically 4–7 paragraphs."
            )

            prompt = f"""
{history_text}

---
Relevant document excerpts:
{context}
---

User question: {query}

Provide a detailed, well-organized answer based on the documents above.
Cover:
1. Direct answer to the question
2. Relevant legal provisions or clauses from the documents
3. Implications and what this means practically
4. Any exceptions, limitations, or important caveats
5. A brief summary / key takeaways
"""

            messages = build_langchain_messages(history, system_prompt)
            messages.append(HumanMessage(content=prompt))

            response = llm.invoke(messages)
            answer = response.content

        # ─── Save to history ─────────────────────────────────────────────────
        add_to_history(user_id, "user", query)
        add_to_history(user_id, "assistant", answer)

        return answer

    except Exception as e:
        print("AGENT ERROR:", e)
        return "An error occurred while processing your request. Please try again."