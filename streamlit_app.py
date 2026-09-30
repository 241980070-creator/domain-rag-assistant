import os
import tempfile
import uuid

import streamlit as st

from dotenv import load_dotenv

from ingest import index_document
from robust_pipeline import stream_answer


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(".env")


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Domain RAG Assistant",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


if "messages" not in st.session_state:
    st.session_state.messages = []


if "processed_files" not in st.session_state:
    st.session_state.processed_files = []


# ============================================================
# TITLE
# ============================================================

st.title("📄 Domain-Specific RAG Assistant")

st.caption(
    "Upload documents and ask questions based on their content."
)


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_TYPES = [
    "pdf",
    "docx",
    "txt",
    "md",
    "csv",
    "xlsx",
    "xls",
    "json",
    "pptx",
]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📁 Document Upload")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=SUPPORTED_TYPES,
        help=(
            "Supported: PDF, Word, TXT, Markdown, "
            "CSV, Excel, JSON and PowerPoint."
        ),
    )

    if uploaded_file:

        st.write(
            f"**Selected:** `{uploaded_file.name}`"
        )

        if st.button(
            "Process Document",
            type="primary",
            use_container_width=True,
        ):

            temp_path = None

            with st.spinner(
                "Reading, chunking and indexing document..."
            ):

                try:

                    # --------------------------------------------
                    # Save uploaded file temporarily
                    # --------------------------------------------

                    file_extension = os.path.splitext(
                        uploaded_file.name
                    )[1]

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=file_extension,
                    ) as temp_file:

                        temp_file.write(
                            uploaded_file.getvalue()
                        )

                        temp_path = temp_file.name


                    # --------------------------------------------
                    # Run existing ingestion pipeline
                    # --------------------------------------------

                    result = index_document(
                        file_path=temp_path,
                        session_id=st.session_state.session_id,
                    )


                    # --------------------------------------------
                    # Remove temporary file
                    # --------------------------------------------

                    if temp_path and os.path.exists(temp_path):

                        os.remove(temp_path)

                        temp_path = None


                    # --------------------------------------------
                    # Save processed filename
                    # --------------------------------------------

                    filename = uploaded_file.name

                    if filename not in st.session_state.processed_files:

                        st.session_state.processed_files.append(
                            filename
                        )


                    # --------------------------------------------
                    # Success message
                    # --------------------------------------------

                    st.success(
                        f"Successfully indexed `{filename}`"
                    )


                    st.write(
                        f"Documents loaded: "
                        f"{result.get('documents', 0)}"
                    )

                    st.write(
                        f"Chunks indexed: "
                        f"{result.get('chunks', 0)}"
                    )

                    st.write(
                        f"Processing time: "
                        f"{result.get('total_time', 0)} seconds"
                    )


                except Exception as e:

                    # --------------------------------------------
                    # Cleanup temporary file if something fails
                    # --------------------------------------------

                    if temp_path and os.path.exists(temp_path):

                        os.remove(temp_path)


                    st.error(
                        "Document processing failed."
                    )

                    st.exception(e)


    # ========================================================
    # ACTIVE DOCUMENTS
    # ========================================================

    if st.session_state.processed_files:

        st.divider()

        st.subheader("📚 Active Documents")

        for filename in st.session_state.processed_files:

            st.markdown(
                f"✅ `{filename}`"
            )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_question = st.chat_input(
    "Ask a question about your uploaded documents..."
)


if user_question:

    user_question = user_question.strip()


    if not user_question:

        st.warning(
            "Please enter a question."
        )

        st.stop()


    # ========================================================
    # USER MESSAGE
    # ========================================================

    st.session_state.messages.append({
        "role": "user",
        "content": user_question,
    })


    with st.chat_message("user"):

        st.markdown(
            user_question
        )


    # ========================================================
    # ASSISTANT RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        placeholder = st.empty()

        full_response = ""


        try:

            # ------------------------------------------------
            # Directly call existing RAG pipeline
            # ------------------------------------------------

            for token in stream_answer(
                question=user_question,
                session_id=st.session_state.session_id,
                history=st.session_state.messages[:-1],
            ):

                full_response += token

                placeholder.markdown(
                    full_response + "▌"
                )


            # ------------------------------------------------
            # Final response
            # ------------------------------------------------

            placeholder.markdown(
                full_response
            )


            # ------------------------------------------------
            # Save assistant message
            # ------------------------------------------------

            if full_response:

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                })


        except Exception as e:

            placeholder.error(
                "❌ RAG/Groq Error"
            )

            st.exception(e)
