import json
import uuid

import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Domain RAG Assistant",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# BACKEND
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# SESSION STATE
# ============================================================

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
    )


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
# SUPPORTED EXTENSIONS
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

            with st.spinner(
                "Reading, chunking and indexing document..."
            ):

                try:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                            or "application/octet-stream",
                        )
                    }

                    data = {
                        "session_id":
                            st.session_state.session_id
                    }

                    response = requests.post(
                        f"{BACKEND_URL}/api/upload",
                        files=files,
                        data=data,
                        timeout=300,
                    )

                    if response.status_code == 200:

                        result = response.json()

                        filename = uploaded_file.name

                        if filename not in st.session_state.processed_files:

                            st.session_state.processed_files.append(
                                filename
                            )

                        st.success(
                            f"Successfully indexed `{filename}`"
                        )

                        st.write(
                            f"Documents loaded: "
                            f"{result.get('documents_loaded', 0)}"
                        )

                        st.write(
                            f"Chunks indexed: "
                            f"{result.get('chunks_indexed', 0)}"
                        )

                    else:

                        try:
                            error_data = response.json()

                            error_message = error_data.get(
                                "detail",
                                response.text
                            )

                        except Exception:

                            error_message = response.text

                        st.error(
                            "Upload failed:\n\n"
                            f"{error_message}"
                        )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Could not connect to FastAPI.\n\n"
                        "Make sure app.py is running."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "The document took too long to process."
                    )

                except Exception as e:

                    st.error(
                        f"Unexpected error: "
                        f"{type(e).__name__}: {str(e)}"
                    )


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


    # ========================================================
    # CONNECTION CHECK
    # ========================================================

    st.divider()

    if st.button(
        "Check Backend",
        use_container_width=True
    ):

        try:

            response = requests.get(
                f"{BACKEND_URL}/health",
                timeout=10
            )

            if response.status_code == 200:

                st.success(
                    "FastAPI is running."
                )

            else:

                st.error(
                    f"Backend returned "
                    f"{response.status_code}"
                )

        except Exception as e:

            st.error(
                f"Backend unavailable: {e}"
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

            payload = {
                "session_id":
                    st.session_state.session_id,

                "question":
                    user_question,
            }

            with requests.post(
                f"{BACKEND_URL}/api/chat/stream",
                json=payload,
                stream=True,
                timeout=300,
            ) as response:

                if response.status_code != 200:

                    try:

                        error_data = response.json()

                        error_message = error_data.get(
                            "detail",
                            response.text
                        )

                    except Exception:

                        error_message = response.text

                    st.error(
                        f"Backend Error "
                        f"({response.status_code}): "
                        f"{error_message}"
                    )

                    st.stop()


                # =================================================
                # SERVER-SENT EVENTS
                # =================================================

                for line in response.iter_lines(
                    decode_unicode=True
                ):

                    if not line:

                        continue

                    if not line.startswith(
                        "data: "
                    ):

                        continue

                    data_string = line[
                        len("data: "):
                    ].strip()


                    # ================================
                    # END OF STREAM
                    # ================================

                    if data_string == "[DONE]":

                        break


                    # ================================
                    # PARSE EVENT
                    # ================================

                    try:

                        data = json.loads(
                            data_string
                        )

                    except json.JSONDecodeError:

                        full_response += data_string

                        placeholder.markdown(
                            full_response + "▌"
                        )

                        continue


                    # ================================
                    # BACKEND ERROR
                    # ================================

                    if "error" in data:

                        error_message = data["error"]

                        full_response = (
                            "❌ **RAG/Groq Error:**\n\n"
                            f"`{error_message}`"
                        )

                        placeholder.markdown(
                            full_response
                        )

                        break


                    # ================================
                    # TOKEN
                    # ================================

                    token = data.get(
                        "token",
                        ""
                    )

                    if token:

                        full_response += token

                        placeholder.markdown(
                            full_response + "▌"
                        )


                # =================================================
                # FINAL RESPONSE
                # =================================================

                placeholder.markdown(
                    full_response
                )


                # =================================================
                # SAVE ASSISTANT MESSAGE
                # =================================================

                if full_response:

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                    })


        except requests.exceptions.ConnectionError:

            placeholder.error(
                "❌ Could not connect to FastAPI.\n\n"
                "Make sure `app.py` is running."
            )


        except requests.exceptions.Timeout:

            placeholder.error(
                "❌ The request timed out."
            )


        except Exception as e:

            placeholder.error(
                "❌ Unexpected error:\n\n"
                f"{type(e).__name__}: {str(e)}"
            )