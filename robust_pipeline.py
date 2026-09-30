import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from ingest import (
    get_vector_store,
    retrieve_documents,
    format_context,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing from .env"
    )


# ============================================================
# GROQ MODEL
# ============================================================

MODEL_NAME = "openai/gpt-oss-20b"


llm = ChatGroq(
    model=MODEL_NAME,
    groq_api_key=GROQ_API_KEY,
    temperature=0.0,
    streaming=True,
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a document-based RAG assistant.

Answer using the retrieved document context.

Rules:
- Use only information supported by the context.
- Do not invent facts.
- If the answer is not in the context, say so clearly.
- You may combine information from multiple sources.
- For calculations, calculate carefully.
- Keep answers clear and concise.

Retrieved context:

{context}
"""





# ============================================================
# BUILD MESSAGE
# ============================================================

def build_messages(
    question: str,
    context: str,
    history=None
):
    """
    Build the messages sent to Groq.
    """

    messages = [
        (
            "system",
            SYSTEM_PROMPT.format(
                context=context
            )
        )
    ]

    if history:

        for message in history:

            role = message.get("role")
            content = message.get("content")

            if role in ["user", "assistant"]:

                messages.append(
                    (
                        role,
                        content
                    )
                )

    messages.append(
        (
            "human",
            question
        )
    )

    return messages


# ============================================================
# RETRIEVAL
# ============================================================

def get_context(
    question: str,
    session_id: str,
    k: int = 3
):
    """
    Retrieve relevant document chunks.
    """

    documents = retrieve_documents(
        question=question,
        session_id=session_id,
        k=k
    )

    return format_context(documents)


# ============================================================
# STREAM ANSWER
# ============================================================

def stream_answer(
    question: str,
    session_id: str,
    history=None
):
    """
    Retrieve context and stream the Groq response.
    """

    context = get_context(
        question=question,
        session_id=session_id,
        k=5
    )

    messages = build_messages(
        question=question,
        context=context,
        history=history
    )

    for chunk in llm.stream(messages):

        if not chunk:
            continue

        content = getattr(
            chunk,
            "content",
            ""
        )

        if isinstance(content, str):
            if content:
                yield content

        elif isinstance(content, list):

            for item in content:

                if isinstance(item, dict):

                    text = item.get(
                        "text",
                        ""
                    )

                    if text:
                        yield text