# Handles the meeting transcript vector database:
# creates embeddings, stores transcript chunks in ChromaDB,
# loads the saved vector store, and provides a retriever
# for finding relevant transcript chunks.


from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from core.models import get_embeddings


CHROMA_DIR = "vector_db"
#CHROMA_DIR = "test_vector_db"
COLLECTION_NAME = "meeting_transcript"


def build_vector_store(transcript: str) -> Chroma:
    # Splits the transcript into small chunks, converts them into embeddings,
    # and stores them in a persistent ChromaDB vector database.
    print("Building vector store...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(transcript)

    print(f"Transcript length: {len(transcript)} characters")
    print(f"Created {len(chunks)} transcript chunks")

    docs = [
        Document(
            page_content=chunk,
            metadata={"chunk_index": i}
        )
        for i, chunk in enumerate(chunks)
    ]

    print("Creating Chroma vector store...")

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR
    )
    
    print("Chroma vector store created!")
    
    return vector_store


def load_vector_store() -> Chroma:
    # Loads the existing ChromaDB vector database from disk.
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR
    )


def get_retriever(vector_store: Chroma, k: int = 4):
    # Creates a retriever that finds the most relevant transcript chunks.
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )