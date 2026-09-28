# Extracts actionable information from meeting transcripts:
# action items, key decisions, and unresolved questions.


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from core.models import get_llm


def build_chain(system_prompt: str):
    # Creates a reusable LLM chain using the given instruction/prompt.
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{text}")
    ])

    return prompt | llm | StrOutputParser()


def extract_action_items(transcript: str) -> str:
    # Extracts tasks from the transcript along with their owner and deadline.
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    )

    return chain.invoke({"text": transcript})


def extract_key_decisions(transcript: str) -> str:
    # Extracts the important decisions made during the meeting.
    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )

    return chain.invoke({"text": transcript})


def extract_questions(transcript: str) -> str:
    # Extracts unresolved questions and topics that need follow-up.
    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )

    return chain.invoke({"text": transcript})