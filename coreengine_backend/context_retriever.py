import os
import chromadb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "vector_store")

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

nec_collection = client.get_or_create_collection(name="nec_docs")
wattmonk_collection = client.get_or_create_collection(name="wattmonk_docs")


def retrieve_context(query: str, intent: str, top_k: int = 3) -> dict:
    """
    Retrieves relevant context from ChromaDB based on intent.
    """

    if intent == "general":
        return {
            "context": "",
            "source": "General",
            "confidence": 1.0
        }

    if intent == "nec":
        results = nec_collection.query(
            query_texts=[query],
            n_results=top_k
        )
        documents = results.get("documents", [])
        documents = documents[0] if documents else []
        context = "\n\n".join(documents) if documents else ""

        return {
            "context": context,
            "source": "NEC",
            "confidence": 0.85 if context else 0.30
        }

    if intent == "wattmonk":
        results = wattmonk_collection.query(
            query_texts=[query],
            n_results=top_k
        )
        documents = results.get("documents", [])
        documents = documents[0] if documents else []
        context = "\n\n".join(documents) if documents else ""

        return {
            "context": context,
            "source": "Wattmonk",
            "confidence": 0.85 if context else 0.30
        }

    return {
        "context": "",
        "source": "Unknown",
        "confidence": 0.0
    }


if __name__ == "__main__":
    print("Using Chroma path:", CHROMA_DB_PATH)

    print("\n=== NEC TEST ===")
    nec_result = retrieve_context("What does NEC say about grounding?", "nec")
    print(nec_result["context"][:1500])

    print("\n=== WATTMONK TEST ===")
    wattmonk_result = retrieve_context("What does Wattmonk do?", "wattmonk")
    print(wattmonk_result["context"][:1500])
