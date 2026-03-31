import os
import chromadb
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "vector_store")

NEC_PDF_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "nec",
    "2017-NEC-Code-2 (2) (1) (1).pdf"
)

WATTMONK_PDF_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "wattmonk",
    "Wattmonk Information.pdf"
)

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

nec_collection = client.get_or_create_collection(name="nec_docs")
wattmonk_collection = client.get_or_create_collection(name="wattmonk_docs")


def is_junk_nec_page(text: str) -> bool:
    """
    Filters obvious front-matter / disclaimer pages from NEC PDF.
    """
    if not text or not text.strip():
        return True

    lowered = text.lower()

    junk_markers = [
        "isbn",
        "copyright",
        "national fire protection association",
        "important notices and disclaimers",
        "notice and disclaimer of liability",
        "one batterymarch park",
        "registered trademarks",
        "nfpa standards",
        "quincy, massachusetts"
    ]

    return any(marker in lowered for marker in junk_markers)


def extract_text_from_pdf(pdf_path: str, source_name: str, start_page: int = 0, end_page: int = None) -> str:
    """
    Reads text from a PDF file.
    For NEC, filters obvious junk/disclaimer pages.
    """
    reader = PdfReader(pdf_path)
    full_text = ""

    total_pages = len(reader.pages)

    if end_page is None or end_page > total_pages:
        end_page = total_pages

    for page_num in range(start_page, end_page):
        page = reader.pages[page_num]
        page_text = page.extract_text()

        if not page_text:
            continue

        if source_name == "NEC" and is_junk_nec_page(page_text):
            continue

        full_text += page_text + "\n"

    return full_text


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list:
    """
    Splits text into overlapping chunks.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def clear_collection(collection):
    """
    Deletes all existing documents from a collection before re-ingesting.
    """
    existing = collection.get()

    if existing and "ids" in existing and existing["ids"]:
        collection.delete(ids=existing["ids"])


def ingest_pdf_to_collection(pdf_path: str, collection, source_name: str):
    """
    Extracts text, chunks it, and stores it in ChromaDB.
    """
    print(f"\nReading PDF: {pdf_path}")

    if source_name == "NEC":
        text = extract_text_from_pdf(
            pdf_path=pdf_path,
            source_name=source_name,
            start_page=0,
            end_page=150
        )
    else:
        text = extract_text_from_pdf(
            pdf_path=pdf_path,
            source_name=source_name
        )

    if not text.strip():
        print(f"No usable text found in {pdf_path}")
        return

    chunks = chunk_text(text)

    clear_collection(collection)

    for idx, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{source_name}_{idx}"],
            metadatas=[{"source": source_name, "chunk_id": idx}]
        )

    print(f"Stored {len(chunks)} chunks for {source_name}")


if __name__ == "__main__":
    ingest_pdf_to_collection(NEC_PDF_PATH, nec_collection, "NEC")
    ingest_pdf_to_collection(WATTMONK_PDF_PATH, wattmonk_collection, "Wattmonk")

    print("\nIngestion completed successfully.")
    print("NEC count:", nec_collection.count())
    print("Wattmonk count:", wattmonk_collection.count())

    sample_nec = nec_collection.get(limit=2)
    sample_wattmonk = wattmonk_collection.get(limit=2)

    print("\nSample NEC chunk:")
    if sample_nec.get("documents"):
        print(sample_nec["documents"][0][:1000])

    print("\nSample Wattmonk chunk:")
    if sample_wattmonk.get("documents"):
        print(sample_wattmonk["documents"][0][:1000])
