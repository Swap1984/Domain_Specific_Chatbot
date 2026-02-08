# Document-Specific Chatbot

A document-based chatbot built with **Streamlit** and **sentence-transformers**.
Upload any PDF, DOCX, or TXT file and ask questions interactively.

## Features

- Upload multiple documents dynamically.
- Supports PDF, DOCX, TXT formats.
- Embedding-based similarity search for relevant answers.
- Streamlit frontend with chat history.

## Quickstart

1. Clone the repository:

```bash
git clone <your-repo-url>
cd Domain_Specific_Chatbot
```

2. Create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the Streamlit app:

```bash
streamlit run src/app.py
```

## Data Folder

Sample documents can be placed in the `data/` folder. See `data/README.md` for expectations and guidelines.

## Observations and Fixes (Project Notes)

### What I observed
- Answers felt keyword-driven and sometimes irrelevant to the user question.
- First chunks often came from the table of contents (TOC), which is not useful for Q&A.
- PDF text had broken lines and noisy formatting, causing low-quality chunks.

### What I changed to correct it
- Added **text normalization** before chunking to merge broken lines and reduce noise.
- Improved **chunking strategy** (paragraph-first + sentence split for long blocks).
- Added **TOC filtering** to skip low-value chunks with short lines and heavy digits.
- Added **sentence-level extraction** so the answer comes from the most relevant sentences, not whole chunks.
- Added **embedding caching** to speed up repeated queries on the same document.

### Current limitations
- This is still retrieval-only (no reasoning/generation step), so answers can feel robotic.
- Relevance is limited by embedding similarity alone.

## Upgrade Roadmap (Next Steps)

### 1) Retrieval improvements (no LLM required)
- Add **cross-encoder re-ranking** (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) to re-score top chunks.
- Add **hybrid search** (BM25 + embeddings) to balance keyword and semantic relevance.

### 2) Add a generator (RAG)
- Use a local LLM (via `ollama` or `llama.cpp`) to synthesize answers from retrieved chunks.
- Return answers with **citations** (chunk IDs or page numbers) for trust.

### 3) Quality & usability
- Store chunk metadata (page number, section heading).
- Improve UI to show source snippets and confidence.
- Add evaluation samples to test answer correctness over time.

## Before/After Example

**Before (basic chunking + raw chunk answer):**
- Q: "What is supervised learning?"
- A: "Core Machine Learning Concepts ... Supervised Learning ... (table of contents-like content)"

**After (normalized text + better chunking + sentence extraction | source: `data/machine_learning.docx`):**
- Q: "What is supervised learning?"
- A: "Supervised Learning: Trains models on labeled data to map inputs to known outputs, commonly used for classification and regression."
