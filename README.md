# NovaBank Internal Policy Copilot (Agentic RAG)

An AI assistant that answers NovaBank employees' questions about internal procedures. It searches the company's private documents first, checks whether the evidence is good enough, and only uses web search when it is not.

**Stack:** LangGraph · FastAPI · Pinecone · Groq · Tavily · HuggingFace Embeddings · HTML/CSS/JavaScript

> NovaBank is a fictional company created for demonstration purposes. 

---

## 1. The Problem

NovaBank is a fictional bank with 3,000 employees. Its compliance and operations teams maintain many documents: loan procedures, fraud-reporting steps, data-protection rules, and customer-onboarding checks.

Employees keep asking the same questions because:

- They do not know which document has the answer.
- Keyword search returns too many results.
- A normal chatbot can make up an answer, which is risky in a bank.
- Some questions need current public information, such as new regulations.

## 2. The Solution

A copilot that:

1. Searches the trusted private knowledge base first.
2. Checks whether the retrieved evidence is good enough.
3. Uses web search only when private knowledge is not enough.
4. Rewrites weak queries and retries (with a retry limit).
5. Generates answers based on the evidence found.
6. Shows its decision path so users can see why it answered the way it did.
7. Lets authorized staff upload new documents without changing any code.

## 3. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent workflow | LangGraph | Stateful routing and conditional decisions |
| LLM | Groq | Routing, grading, query rewriting, answers |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` | Local 384-dimensional embeddings |
| Vector DB | Pinecone | Stores the private knowledge base |
| Web search | Tavily | Fallback for current information |
| Backend | FastAPI | REST API |
| Frontend | HTML/CSS/JavaScript | Chat interface |
| Audit | SQLite | Logs each decision path |
| Packaging | Docker | Reproducible deployment |

## 4. Project Structure

```text
app/
├── api/routes.py          # Chat, health and ingestion endpoints
├── core/                  # Config and logging
├── rag/
│   ├── state.py           # LangGraph state
│   ├── vectorstore.py     # Pinecone + embeddings
│   └── workflow.py        # The agent graph
├── services/
│   ├── audit.py           # SQLite audit log
│   └── ingestion.py       # Load, chunk and index documents
└── main.py                # FastAPI app
data/sample_kb/            # NovaBank sample documents
static/ · templates/       # Web UI
tests/                     # Ingestion tests
ingest_sample_kb.py        # Loads the sample documents
run.py                     # Starts the app
```

## 5. Run It Locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (create a .env file, never commit it)
#    GROQ_API_KEY, TAVILY_API_KEY, PINECONE_API_KEY
#    PINECONE_INDEX_NAME=novabank-policy-rag   (dimension 384)
#    PINECONE_NAMESPACE=novabank-kb
#    ADMIN_API_KEY=<a long random value>

# 4. Load the sample knowledge base
python ingest_sample_kb.py

# 5. Start the app
python run.py
```

Open `http://127.0.0.1:8000` for the app, or `http://127.0.0.1:8000/docs` for the API docs.

## 6. Adding Documents

Authorized staff can upload `.pdf`, `.txt`, `.md` or `.docx` files from the sidebar (protected by an admin key). The backend validates the file, extracts the text, splits it into chunks, embeds them, and indexes them in Pinecone. The new content is searchable right away.

## 7. API

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Health check |
| `POST /api/chat` | Ask a question. Returns the answer, the source used, and the decision trace |
| `POST /api/ingest` | Upload a document (requires the `X-Admin-Key` header) |

Example response from `/api/chat`:

```json
{
  "answer": "...",
  "source_used": "private_kb",
  "trace": [
    "Router → KB",
    "Private KB retrieval → 4 chunks",
    "KB evidence grade → GOOD",
    "Answer generation → PRIVATE KB"
  ],
  "citations": []
}
```