# Multi-Context RAG Chatbot

This project is a context-aware AI chatbot that can handle queries from different domains like general questions, NEC (electrical code), and Wattmonk company data.

The main idea was to build something that doesn’t just give generic answers, but actually understands the context of the question and pulls relevant information from specific knowledge sources.

---

DEMO LINK :- https://ai-intern-assignment-submission---kunal-itepvxdjbzc3wz8ejdbdps.streamlit.app/

## What this chatbot does

* Answers general questions using an LLM
* Detects whether the query is related to NEC or Wattmonk
* Retrieves relevant information from stored documents using a vector database
* Supports follow-up questions (basic context awareness)

---

## Tech Stack

* Python
* FastAPI (backend structure)
* Streamlit (UI)
* ChromaDB (vector database)
* Gemini API (LLM for response generation)

---

## How it works (simple idea)

1. User asks a question
2. System detects the intent (general / NEC / Wattmonk)
3. If domain-specific → relevant chunks are retrieved from the vector database
4. Context is passed to the LLM
5. Final response is generated

---

## Project Structure

```
coreengine_backend/
│   app_server.py
│   intent_router.py
│   context_retriever.py
│   response_engine.py
│   knowledge_ingestor.py
│
ui/
│   chat_interface.py
│
knowledge_base/
│   nec/
│   wattmonk/
│
vector_store/  (generated at runtime)
│
project_docs/
```

---

## Setup Instructions

### 1. Clone the repository

```
git clone <your_repo_link>
cd project_folder
```

---

### 2. Install dependencies

```
pip install -r requirements.txt
```

---

### 3. Set API key

#### Windows

```
set GEMINI_API_KEY=your_api_key
```

#### Linux/macOS

```
export GEMINI_API_KEY=your_api_key
```

---

### 4. Run ingestion (first time only)

```
python coreengine_backend/knowledge_ingestor.py
```

This step creates the vector database from the PDFs.

---

### 5. Run the application

```
streamlit run ui/chat_interface.py
```

---

## Example queries

### General

* What is machine learning?

### NEC

* What does NEC say about grounding?
* Explain Article 250 in NEC

### Wattmonk

* What does Wattmonk do?
* Tell me about Wattmonk services

---

## Deployment Notes

* `vector_store/` is not included in the repository
* It is generated automatically from the PDFs
* API keys are handled using environment variables or Streamlit secrets


## Author

Kunal
