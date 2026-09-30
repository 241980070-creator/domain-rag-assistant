\# Domain RAG Assistant



A document-based Retrieval-Augmented Generation (RAG) assistant that allows users to upload documents and ask questions based on their content.



\## Overview



The Domain RAG Assistant is an AI-powered document question-answering application designed to retrieve relevant information from uploaded documents and generate grounded responses.



The application supports multiple document formats and combines document processing, embeddings, vector search, retrieval, and large language models into a complete RAG pipeline.



\## Features



\* Upload and process multiple document formats

\* Ask questions about uploaded documents

\* Retrieval-Augmented Generation (RAG) pipeline

\* Semantic document retrieval

\* Session-based document collections

\* Streaming AI responses

\* Grounded responses based on retrieved document context

\* Support for structured and unstructured documents

\* FastAPI backend

\* Streamlit interactive interface



\## Supported File Formats



\* PDF

\* DOCX

\* TXT

\* Markdown

\* CSV

\* XLSX

\* XLS

\* JSON

\* PowerPoint (PPTX)



\## Technology Stack



| Technology   | Purpose                               |

| ------------ | ------------------------------------- |

| Python       | Core programming language             |

| FastAPI      | Backend API                           |

| Streamlit    | Interactive web interface             |

| LangChain    | RAG pipeline and document processing  |

| ChromaDB     | Vector database and similarity search |

| Hugging Face | Sentence-transformer embeddings       |

| Groq         | Large language model inference        |

| Pandas       | CSV and Excel processing              |



\## RAG Pipeline



The application follows this general workflow:



```text

User uploads document

&#x20;       ↓

Document loading

&#x20;       ↓

Text extraction

&#x20;       ↓

Document chunking

&#x20;       ↓

Hugging Face embeddings

&#x20;       ↓

ChromaDB vector storage

&#x20;       ↓

Similarity retrieval

&#x20;       ↓

Retrieved context

&#x20;       ↓

Groq LLM

&#x20;       ↓

Generated response

```



\## Document Processing



The ingestion pipeline handles different document types using format-specific loaders.



For structured data such as CSV files, rows are grouped before embedding to reduce the number of individual embeddings required during indexing.



This improves ingestion performance when processing larger tabular datasets while preserving the information needed for retrieval.



\## Example Use Case



A user can upload a document such as a PDF containing technical or business information and then ask questions about its contents.



For example:



```text

User:

What are the main objectives described in the document?



Assistant:

Provides an answer based on the retrieved document content.

```



The system is designed to avoid generating information that is not supported by the retrieved document context.



\## Project Structure



```text

domain-rag-assistant/

│

├── app.py

├── ingest.py

├── robust\_pipeline.py

├── streamlit\_app.py

├── requirements.txt

├── README.md

├── .gitignore

└── .python-version

```



\## Running the Project Locally



\### 1. Clone the repository



```bash

git clone https://github.com/YOUR-USERNAME/domain-rag-assistant.git

cd domain-rag-assistant

```



\### 2. Create a virtual environment



```bash

python -m venv venv

```



\### 3. Activate the virtual environment



Windows:



```bash

venv\\Scripts\\activate

```



\### 4. Install dependencies



```bash

pip install -r requirements.txt

```



\### 5. Configure environment variables



Create a `.env` file and add your Groq API key:



```text

GROQ\_API\_KEY=your\_api\_key\_here

```



Do not commit your `.env` file or API keys to GitHub.



\### 6. Start the FastAPI backend



```bash

uvicorn app:app --reload

```



The backend will run locally at:



```text

http://127.0.0.1:8000

```



\### 7. Start the Streamlit application



Open another terminal and run:



```bash

streamlit run streamlit\_app.py

```



The Streamlit application will open in your browser.



\## API Documentation



When the FastAPI backend is running, interactive API documentation is available at:



```text

http://127.0.0.1:8000/docs

```



\## Security



API keys and environment variables should not be committed to the repository.



The following files and directories are excluded from version control:



```text

.env

venv/

\_\_pycache\_\_/

chroma\_db\_robust/

.streamlit/secrets.toml

```



\## Future Improvements



Potential future improvements include:



\* Persistent production vector storage

\* Improved retrieval strategies for structured datasets

\* Authentication and user management

\* Additional document formats

\* Production-scale deployment

\* More advanced evaluation of retrieval and answer quality



\## Author



Built as a Data Science and Generative AI portfolio project.



