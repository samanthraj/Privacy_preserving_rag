# Privacy-Preserving RAG Chatbot

A full-stack AI chatbot that uses Retrieval-Augmented Generation (RAG) to deliver accurate, context-grounded responses — while minimizing hallucination and keeping user data private. Built with a ChatGPT-style interface, powered by Groq and PostgreSQL.

---

## What it does

Most AI chatbots hallucinate because they rely solely on the model's training data. This project solves that by injecting your own documents as context before the model ever generates a response.

There are two core pipelines:

**Data Ingestion Pipeline** — Upload your documents → they get chunked into segments → each chunk is embedded into a vector → stored in a PostgreSQL vector database.

**Query Pipeline** — User sends a message → it gets embedded → similarity search finds the top 5 most relevant chunks from your data → those chunks are passed as context to the Groq LLM along with a structured prompt → the model responds accurately based on your data, not guesswork.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| Frontend | React.js (ChatGPT-style UI) |
| Database | PostgreSQL (via psycopg2) |
| LLM | Groq API |
| Auth | bcrypt password hashing |
| Embeddings | Vector similarity search |

---

## Features

- User registration and login with hashed passwords
- Persistent chat history per user
- RAG pipeline: document ingestion → chunking → embedding → vector search
- Structured prompt filtering to reduce hallucination
- Clear chat functionality
- REST API with clean endpoint separation

---

## Project structure

```
├── app.py          # Flask backend — auth, chat, history endpoints
├── rag.py          # RAG logic — embedding, vector search, LLM call
├── test.py         # Testing utilities
├── requirment.txt  # Python dependencies
└── .gitignore
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/register` | Register a new user |
| POST | `/login` | Login and get user session |
| POST | `/chat` | Send a message, get RAG-powered reply |
| GET | `/history/<user_id>` | Fetch chat history |
| DELETE | `/clear` | Clear chat history for a user |

---

## Getting started

### Prerequisites

- Python 3.9+
- PostgreSQL running locally
- Groq API key

### Setup

```bash
# Clone the repo
git clone https://github.com/samanthraj/Rag_application_to_solve_privacy_and_hallucination.git
cd Rag_application_to_solve_privacy_and_hallucination

# Install dependencies
pip install -r requirment.txt

# Set up PostgreSQL database
# Create a database named 'rag_app' and update credentials in app.py

# Run the backend
python app.py
```

Set your Groq API key as an environment variable or configure it in `rag.py`.

---

## How RAG helps

| Without RAG | With RAG |
|---|---|
| Model guesses from training data | Model answers from your actual documents |
| High hallucination risk | Grounded, verifiable responses |
| Requires expensive fine-tuning | Just upload new docs — no retraining |
| Generic answers | Tailored, context-aware replies |

**Limitation:** Response length depends on the model used. Higher-end Groq models produce richer outputs.

---

## Author

**Samanthraj G** — [github.com/samanthraj](https://github.com/samanthraj) | [LinkedIn](https://linkedin.com/in/samanth-raj-garela-80346524a)

*Final year B.Tech Computer Science, ICFAI University Hyderabad*
