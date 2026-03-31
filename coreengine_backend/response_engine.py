from google import genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def build_general_prompt(query: str, chat_history: list = None) -> str:
    history_text = ""

    if chat_history:
        for msg in chat_history[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

    prompt = f"""
You are a helpful AI assistant.

Respond clearly, naturally, and concisely.
If the user is asking a general question, answer using your own knowledge.

Conversation History:
{history_text}

User Question:
{query}
"""
    return prompt


def build_context_prompt(
    query: str, context: str, source: str, chat_history: list = None
) -> str:
    history_text = ""

    if chat_history:
        for msg in chat_history[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"

    prompt = f"""
    You are a context-aware AI assistant.

    Use the provided context as your primary source to answer the question.

    Rules:
    1. Base your answer mainly on the context.
    2. If the context partially answers the question, explain using that information.
    3. You may rephrase and explain the context in simpler words.
    4. Do NOT hallucinate completely new facts.
    5. If nothing relevant is found, then say the information is not available.

    Keep the answer clear, structured, and easy to understand.

    Conversation History:
    {history_text}

    Source:
    {source}

    Retrieved Context:
    {context}

    User Question:
    {query}
    """
    return prompt


def generate_response(
    query: str,
    intent: str,
    context: str = "",
    source: str = "General",
    confidence: float = 1.0,
    chat_history: list = None,
) -> dict:

    if intent == "general":
        prompt = build_general_prompt(query, chat_history)
    else:
        if not context.strip():
            return {
                "answer": f"I could not find relevant information in the {source} knowledge base for this query.",
                "source": source,
                "confidence": 0.30,
                "suggested_questions": [
                    "Can you rephrase the question?",
                    f"Ask something more specific about {source}.",
                ],
            }

        prompt = build_context_prompt(query, context, source, chat_history)

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)

    answer_text = response.text.strip() if response.text else "No response generated."

    suggested_questions = []

    if intent == "nec":
        suggested_questions = [
            "Can you explain this NEC concept in simpler words?",
            "Are there related NEC safety rules?",
        ]
    elif intent == "wattmonk":
        suggested_questions = [
            "Can you tell me more about the company?",
            "What other Wattmonk-related details are available?",
        ]
    else:
        suggested_questions = [
            "Can you explain this in simpler terms?",
            "Can you give a short summary?",
        ]

    return {
        "answer": answer_text,
        "source": source,
        "confidence": confidence,
        "suggested_questions": suggested_questions,
    }
