import os
import sys
import streamlit as st
from coreengine_backend.knowledge_ingestor import initialize_knowledge_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from coreengine_backend.intent_router import detect_intent
from coreengine_backend.context_retriever import retrieve_context
from coreengine_backend.response_engine import generate_response


if "db_initialized" not in st.session_state:
    with st.spinner("Initializing knowledge base..."):
        initialize_knowledge_base()
    st.session_state.db_initialized = True

st.set_page_config(
    page_title="Multi-Context RAG Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Multi-Context RAG Chatbot")
st.caption("Ask general questions, NEC-related queries, or Wattmonk-specific questions.")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_context" not in st.session_state:
    st.session_state.last_context = None


def run_chat_pipeline(query, chat_history, last_context):
    intent_result = detect_intent(query, last_context)
    intent = intent_result["intent"]

    retrieved = retrieve_context(query, intent)

    response = generate_response(
        query=query,
        intent=intent,
        context=retrieved["context"],
        source=retrieved["source"],
        confidence=retrieved["confidence"],
        chat_history=chat_history
    )

    return {
        "query": query,
        "intent": intent,
        "intent_reason": intent_result["reason"],
        "is_followup": intent_result["is_followup"],
        "answer": response["answer"],
        "source": response["source"],
        "confidence": response["confidence"],
        "suggested_questions": response["suggested_questions"]
    }


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            st.caption(
                f"Source: {msg.get('source', '')} | Confidence: {int(msg.get('confidence', 0) * 100)}%"
            )
            st.caption(f"Detected Intent: {msg.get('intent', '')}")

            if msg.get("suggested_questions"):
                st.markdown("**Suggested follow-up questions:**")
                for q in msg["suggested_questions"]:
                    st.write(f"- {q}")


user_input = st.chat_input("Type your question here...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    backend_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]

    try:
        result = run_chat_pipeline(
            query=user_input,
            chat_history=backend_history,
            last_context=st.session_state.last_context
        )

        assistant_message = {
            "role": "assistant",
            "content": result["answer"],
            "source": result["source"],
            "confidence": result["confidence"],
            "intent": result["intent"],
            "suggested_questions": result["suggested_questions"]
        }

        st.session_state.messages.append(assistant_message)
        st.session_state.last_context = result["intent"]

        with st.chat_message("assistant"):
            st.markdown(result["answer"])
            st.caption(
                f"Source: {result['source']} | Confidence: {int(result['confidence'] * 100)}%"
            )
            st.caption(f"Detected Intent: {result['intent']}")

            if result["suggested_questions"]:
                st.markdown("**Suggested follow-up questions:**")
                for q in result["suggested_questions"]:
                    st.write(f"- {q}")

    except Exception as e:
        st.error(f"Error: {str(e)}")


with st.sidebar:
    st.header("Quick Actions")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_context = None
        st.rerun()

    st.markdown("---")
    st.subheader("Sample Queries")

    st.markdown("**General**")
    st.write("- What is machine learning?")
    st.write("- Explain deep learning in simple words")

    st.markdown("**NEC**")
    st.write("- What does NEC say about grounding?")
    st.write("- Explain Article 250 in NEC")

    st.markdown("**Wattmonk**")
    st.write("- What does Wattmonk do?")
    st.write("- Tell me about Wattmonk services")
