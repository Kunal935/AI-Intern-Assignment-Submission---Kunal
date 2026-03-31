from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from intent_router import detect_intent
from context_retriever import retrieve_context
from response_engine import generate_response


app = FastAPI(title="Multi-Context RAG Chatbot API")


class ChatRequest(BaseModel):
    query: str
    chat_history: List[Dict[str, Any]] = []
    last_context: Optional[str] = None


@app.get("/")
def home():
    return {"message": "RAG Chatbot API is running successfully."}


@app.post("/chat")
def chat(request: ChatRequest):
    intent_result = detect_intent(request.query, request.last_context)
    intent = intent_result["intent"]

    retrieved = retrieve_context(request.query, intent)

    print("\n=== DEBUG REQUEST ===")
    print("Query:", request.query)
    print("Intent:", intent)
    print("Retrieved source:", retrieved["source"])
    print("Retrieved confidence:", retrieved["confidence"])
    print("Retrieved context preview:", retrieved["context"][:1000] if retrieved["context"] else "EMPTY")
    print("=====================\n")

    response = generate_response(
        query=request.query,
        intent=intent,
        context=retrieved["context"],
        source=retrieved["source"],
        confidence=retrieved["confidence"],
        chat_history=request.chat_history
    )

    return {
        "query": request.query,
        "intent": intent,
        "intent_reason": intent_result["reason"],
        "is_followup": intent_result["is_followup"],
        "answer": response["answer"],
        "source": response["source"],
        "confidence": response["confidence"],
        "suggested_questions": response["suggested_questions"]
    }