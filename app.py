import os
import json
import tempfile
from typing import Dict

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from ingest import (
    SUPPORTED_EXTENSIONS,
    index_document,
)

from robust_pipeline import stream_answer


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(".env")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Domain RAG Assistant API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# SESSION CHAT HISTORY
# ============================================================

session_history: Dict[
    str,
    list
] = {}


def get_history(session_id: str):

    if session_id not in session_history:

        session_history[session_id] = []

    return session_history[session_id]


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "service": "Domain RAG Assistant API",
    }


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

@app.get("/supported-files")
async def supported_files():

    return {
        "supported_extensions": sorted(
            list(SUPPORTED_EXTENSIONS)
        )
    }


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@app.post("/api/upload")
async def upload_document(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and index a document.

    Flow:

    Streamlit
        ↓
    FastAPI
        ↓
    Temporary file
        ↓
    ingest.py
        ↓
    Loader
        ↓
    Chunking
        ↓
    Embeddings
        ↓
    User-specific Chroma
    """

    if not session_id.strip():

        raise HTTPException(
            status_code=400,
            detail="session_id is required."
        )

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename was provided."
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Supported types are: "
                f"{sorted(SUPPORTED_EXTENSIONS)}"
            )
        )

    temp_path = None

    try:

        file_contents = await file.read()

        if not file_contents:

            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temporary_file:

            temporary_file.write(
                file_contents
            )

            temp_path = temporary_file.name

        result = index_document(
            file_path=temp_path,
            session_id=session_id,
        )

        return {
            "status": "success",
            "filename": file.filename,
            "file_type": extension,
            "documents_loaded": result["documents"],
            "chunks_indexed": result["chunks"],
            "collection": result["collection"],
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Document processing failed: "
                f"{type(e).__name__}: {str(e)}"
            )
        )

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)
            except Exception:
                pass


# ============================================================
# REQUEST MODEL
# ============================================================

class QueryRequest(BaseModel):

    session_id: str

    question: str


# ============================================================
# CHAT STREAM
# ============================================================

@app.post("/api/chat/stream")
async def chat_stream(
    request: QueryRequest
):
    """
    Retrieve relevant chunks and stream answer.
    """

    session_id = request.session_id.strip()
    question = request.question.strip()

    if not session_id:

        raise HTTPException(
            status_code=400,
            detail="session_id is required."
        )

    if not question:

        raise HTTPException(
            status_code=400,
            detail="question cannot be empty."
        )

    history = get_history(session_id)[-6:]

    async def generate():

        complete_answer = ""

        try:

            # Run synchronous generator without
            # blocking the HTTP response structure.
            for token in stream_answer(
                question=question,
                session_id=session_id,
                history=history,
            ):

                complete_answer += token

                data = json.dumps({
                    "token": token
                })

                yield (
                    f"data: {data}\n\n"
                )

            # Save conversation after successful answer.
            history.append({
                "role": "user",
                "content": question,
            })

            history.append({
                "role": "assistant",
                "content": complete_answer,
            })

            # Keep memory bounded.
            if len(history) > 20:

                del history[:-20]

            yield "data: [DONE]\n\n"

        except Exception as e:

            error_message = (
                f"{type(e).__name__}: {str(e)}"
            )

            error_data = json.dumps({
                "error": error_message
            })

            yield (
                f"data: {error_data}\n\n"
            )

            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )