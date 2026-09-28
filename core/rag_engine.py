# Handles the RAG question-answering system:
# retrieves relevant meeting transcript chunks from ChromaDB
# and uses the Groq LLM to answer questions based only on that context.


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from core.models import get_llm
from core.vector_store import (
    build_vector_store,
    load_vector_store,
    get_retriever,
)


def format_docs(docs):
    # Combines the retrieved transcript chunks into one text context.
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(transcript: str):
    # Creates a RAG chain from a new transcript by storing it in ChromaDB
    # and connecting retrieval, prompting, and the Groq LLM.
    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store, k=4)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say:
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}"""
        ),
        ("human", "{question}")
    ])

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain():
    # Loads the existing ChromaDB and creates a RAG chain from the saved data.
    vector_store = load_vector_store()
    retriever = get_retriever(vector_store, k=4)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say:
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}"""
        ),
        ("human", "{question}")
    ])

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question: str) -> str:
    # Sends a question to the RAG chain, prints the answer, and returns it.
    print(f"Question: {question}")

    answer = rag_chain.invoke(question)

    print(f"Answer: {answer}")

    return answer