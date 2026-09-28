# Defines all AI models and API clients used throughout the project.
# Keeping them here avoids repeating model configuration in other files.


import os

from groq import Groq
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings


# Model names
LLM_MODEL = "openai/gpt-oss-120b"
WHISPER_MODEL = os.getenv("GROQ_MODEL", "whisper-large-v3")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# Cached Groq Whisper client
_whisper_client = None


def get_llm():
    # Creates and returns the Groq LLM used for text generation.
    return ChatGroq(
        model=LLM_MODEL,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2
    )


def get_embeddings():
    print("Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )

    print("Embedding model ready")

    return embeddings


def get_whisper_client():
    # Creates the Groq client once and reuses it for transcription.
    global _whisper_client

    if _whisper_client is None:
        print("Connecting to Groq...")

        _whisper_client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        print("Groq client ready")

    return _whisper_client