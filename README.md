# Domain RAG Assistant

A document-based Retrieval-Augmented Generation (RAG) assistant that allows users to upload documents and interact with their content through natural-language questions.

The application combines document processing, semantic embeddings, vector search, and large language models to retrieve relevant information from uploaded files and generate context-grounded responses.

## Live Application

[Open the deployed application](https://domain-rag-assistant-cvwkgsazekrbjxsnw8ccwe.streamlit.app/)

## GitHub Repository

[View the source code](https://github.com/241980070-creator/domain-rag-assistant)

---

## Project Overview

Traditional document search often requires users to manually locate relevant sections of a document.

This project explores a different approach: converting documents into searchable vector representations and using semantic retrieval to identify relevant information before generating an answer with a large language model.

The system is designed to answer questions based on the content of documents provided by the user.

The application currently supports:

* PDF
* DOCX
* TXT
* Markdown
* CSV
* XLSX
* XLS
* JSON
* PowerPoint (PPTX)

---

## System Architecture

The current deployed architecture is:

```text
                         User
                          |
                          v
                 Streamlit Interface
                          |
              +-----------+-----------+
              |                       |
              v                       v
       Document Upload           User Question
              |                       |
              v                       |
       Document Ingestion              |
              |                       |
              v                       |
        Text Extraction                |
              |                       |
              v                       |
        Chunking / Grouping             |
              |                       |
              v                       |
      Hugging Face Embeddings           |
              |                       |
              v                       |
           ChromaDB                    |
              |                       |
              +-----------+------------+
                          |
                          v
                  Semantic Retrieval
                          |
                          v
                  Retrieved Context
                          |
                          v
                     Groq LLM
                          |
                          v
                  Generated Response
```

The project also contains a FastAPI implementation as an alternative backend/API layer, but the currently deployed Streamlit application performs the RAG workflow directly within the Streamlit application.

---

## Core Workflow

### 1. Document Upload

The user uploads a supported document through the Streamlit interface.

### 2. Document Processing

The ingestion pipeline identifies the file type and uses the appropriate loader to extract its contents.

### 3. Chunking

Extracted content is divided into smaller units suitable for embedding and retrieval.

For CSV data, rows are grouped before embedding to reduce the number of individual embedding operations.

### 4. Embedding Generation

The application uses the following Hugging Face Sentence Transformer model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

The model converts document chunks into numerical vector representations.

### 5. Vector Storage

The generated embeddings are stored in ChromaDB.

### 6. Semantic Retrieval

When the user submits a question, the application performs semantic retrieval against the indexed document content and identifies relevant chunks.

### 7. Context Construction

The retrieved information is formatted into context for the language model.

### 8. Response Generation

The retrieved context and user question are passed to a Groq-hosted language model.

The system prompt instructs the model to ground its response in the retrieved context and avoid inventing information that is not present in the retrieved material.

### 9. Streaming Response

The generated response is streamed to the Streamlit interface rather than waiting for the entire response before displaying it.

---

## Technology Stack

| Component               | Technology                         |
| ----------------------- | ---------------------------------- |
| Programming Language    | Python                             |
| Frontend / Interface    | Streamlit                          |
| RAG Framework           | LangChain                          |
| Vector Database         | ChromaDB                           |
| Embedding Model         | Hugging Face Sentence Transformers |
| LLM Provider            | Groq                               |
| Document Processing     | LangChain Community Loaders        |
| Tabular Data Processing | Pandas                             |
| Excel Processing        | OpenPyXL / xlrd                    |
| PDF Processing          | PyPDF / PDFPlumber                 |
| Word Processing         | Docx2txt                           |
| PowerPoint Processing   | python-pptx                        |
| Version Control         | Git / GitHub                       |
| Deployment              | Streamlit Community Cloud          |

---

## Project Structure

```text
domain-rag-assistant/
│
├── streamlit_app.py
├── ingest.py
├── robust_pipeline.py
├── app.py
│
├── day-01-ingest.py
├── day_02_robust_pipeline.py
├── create-samples.py
│
├── test_direct.py
├── test_groq.py
│
├── sample.txt
├── sample.csv
│
├── requirements.txt
├── .gitignore
├── .python-version
└── README.md
```

### Main Files

#### `streamlit_app.py`

Provides the user interface for:

* Uploading documents
* Processing documents
* Displaying indexed-document information
* Asking questions
* Displaying streaming responses
* Maintaining chat history during the session

#### `ingest.py`

Responsible for the document ingestion pipeline, including:

* File-type detection
* Document loading
* Text extraction
* Chunking
* Embedding generation
* ChromaDB indexing

#### `robust_pipeline.py`

Responsible for:

* Loading the Groq API configuration
* Retrieving relevant documents
* Constructing context
* Calling the language model
* Streaming generated responses

#### `app.py`

Contains the FastAPI-based API implementation developed as an alternative backend architecture.

The current Streamlit deployment does not require a separately hosted FastAPI service.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/241980070-creator/domain-rag-assistant.git
```

Move into the project directory:

```bash
cd domain-rag-assistant
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root for local development:

```text
GROQ_API_KEY=your_groq_api_key
```

The `.env` file should never be committed to GitHub.

The repository includes `.env` in `.gitignore` to prevent accidental exposure of API credentials.

For Streamlit Cloud deployment, the API key should be configured through Streamlit Secrets rather than committed to the repository.

---

## Running Locally

Start the Streamlit application:

```bash
streamlit run streamlit_app.py
```

The application will open in your browser.

Upload a supported document, select **Process Document**, and then enter a question about the uploaded content.

---

## Example Workflow

A typical interaction looks like:

```text
Upload Document
       |
       v
Process Document
       |
       v
Extract Content
       |
       v
Create Chunks
       |
       v
Generate Embeddings
       |
       v
Store in ChromaDB
       |
       v
Ask Question
       |
       v
Retrieve Relevant Chunks
       |
       v
Send Context to LLM
       |
       v
Generate Answer
```

---

## Security Considerations

API credentials should never be stored directly in source code or committed to a public repository.

The project uses environment variables for local development and Streamlit Secrets for cloud deployment.

The following files and directories are excluded through `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
chroma_db_robust/
.streamlit/secrets.toml
```

---

## Current Limitations

### Processing Latency

Large CSV and Excel files can take a significant amount of time to process because the system needs to extract the data, prepare it for embedding, generate vector representations, and index the resulting content.

### Initial Model Loading

The embedding model may require additional time to initialize or download in a new deployment environment.

### Retrieval Quality

RAG performance depends on the quality of the retrieved context. Poorly structured documents, ambiguous questions, or information distributed across multiple sections can affect retrieval quality.

### Structured Data

CSV and Excel files contain structured information that is not always best represented through semantic vector search alone.

A future implementation could combine vector retrieval with structured querying or dataframe-based analysis.

### Context Limitations

The system retrieves a limited amount of relevant context rather than passing an entire large document to the language model.

Consequently, information that is not retrieved may not be available to the generation step.

### Production Scalability

The current implementation is primarily a portfolio and development project. Additional architecture and infrastructure would be required for large-scale production workloads.

### Authentication

The current application does not provide a complete authentication and user-management system.

### Evaluation

A formal automated evaluation framework for retrieval quality and answer quality has not yet been implemented.

---

## Future Improvements

Potential future improvements include:

* Hybrid keyword and semantic retrieval
* Improved retrieval and reranking
* More efficient large-file processing
* Better handling of tables and structured datasets
* Structured data querying
* Persistent production-grade vector storage
* Authentication and user management
* Retrieval evaluation metrics
* Answer-quality evaluation
* Observability and monitoring
* Improved document metadata filtering
* More scalable deployment architecture
* Automated testing
* Improved caching and model management

---

## Key Learning Outcomes

This project provided practical experience with:

* Retrieval-Augmented Generation
* Document ingestion pipelines
* Text extraction
* Text chunking
* Embedding models
* Vector databases
* Semantic search
* Context retrieval
* Large language model integration
* Streaming LLM responses
* API development
* Environment-variable management
* Git and GitHub
* Cloud deployment
* Debugging local versus cloud environments

---

## Project Status

The project is currently deployed and functional as a Streamlit application.

The implementation is considered an evolving portfolio project, with further improvements planned around retrieval quality, structured-data processing, scalability, evaluation, and production deployment.

---

## License

This project is intended primarily for educational and portfolio purposes.
