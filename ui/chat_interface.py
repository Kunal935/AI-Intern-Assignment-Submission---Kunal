import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="Multi-Context RAG Chatbot",
    page_icon="💬🤖",
    layout="centered"
)

st.title("Multi-Context RAG Chatbot")
st.caption("Ask general questions, NEC-related queries, or Wattmonk-specific questions.")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_context" not in st.session_state:
    st.session_state.last_context = None


def call_backend(query, chat_history, last_context):
    payload = {
        "query": query,
        "chat_history": chat_history,
        "last_context": last_context if last_context else None
    }

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"Backend Error: {str(e)}")
        return None



for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            st.caption(f"Source: {msg.get('source', '')} | Confidence: {int(msg.get('confidence', 0) * 100)}%")
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

   
    result = call_backend(
        query=user_input,
        chat_history=backend_history,
        last_context=st.session_state.last_context
    )

    if result:
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
            st.caption(f"Source: {result['source']} | Confidence: {int(result['confidence'] * 100)}%")
            st.caption(f"Detected Intent: {result['intent']}")

            if result["suggested_questions"]:
                st.markdown("**Suggested follow-up questions:**")
                for q in result["suggested_questions"]:
                    st.write(f"- {q}")


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
    st.write("- Explain NEC grounding rules")
    st.write("- What does NEC say about electrical safety?")

    st.markdown("**Wattmonk**")
    st.write("- What does Wattmonk do?")
    st.write("- Tell me about Wattmonk services")