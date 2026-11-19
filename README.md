# Customer Support RAG Assistant

A small, local-first portfolio project showing a support chat powered by
retrieval-augmented generation (RAG). FastAPI searches local support articles
with local embeddings, then asks Groq to draft an answer from the best
passages. The API returns the answer, source filenames, and retrieved text.

## What is included

- `GET /health` for a simple health check.
- `POST /documents` to add a UTF-8 `.txt` or `.md` article (up to 1 MB).
- `POST /chat` to retrieve passages and generate a grounded answer.
- `knowledge_base/` with five focused sample support articles.
- A browser chat and document-upload page at `/`.
- A local JSON vector index at `data/vector_store.json`; it is generated when
  the app is used and is not committed.
- `LEARNING_GUIDE.md` explaining the actual code and design choices.

The first request that needs embeddings downloads the FastEmbed model. Internet
access is also needed to call Groq for an answer.

## Requirements

- Python 3.10 or newer
- A Groq API key for answer generation

## Install and configure (Windows PowerShell)

From the project directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The workspace may already have a `.env`. Keep it and make sure it contains your
own `GROQ_API_KEY` and a supported `MODEL_NAME`; do not overwrite it with the
example file. If `.env` does not exist, create it from the template:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set `GROQ_API_KEY` to your own Groq API key. `MODEL_NAME` defaults to
`llama-3.3-70b-versatile`. Do not put the key in `static/index.html` or commit
`.env`. The key stays in the backend process. You can leave the default
`ALLOWED_ORIGINS` for local development.

## Run locally

Start FastAPI in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) for the chat page.
FastAPI's interactive API documentation is at
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). The health endpoint
is [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

## Try it

1. Ask: **How long does a password reset link last?** The answer should use
   `account_access.md` and show its retrieved passage.
2. Ask: **Can I get a refund if I was charged twice?** The cancellation article
   says support must review the billing record; it does not promise a refund.
3. Ask about a topic not covered by the articles, such as **Do you offer
   weekend phone support?** If no passage clears the retrieval threshold, the
   assistant returns its “not enough information” response without calling
   Groq.
4. In **Add a support article**, upload a new `.txt` or `.md` file, then ask a
   question about it. The next chat request embeds the new file before
   retrieval.

Uploads are stored in `knowledge_base/`. Duplicate filenames are rejected, so
choose a new filename for each new article. To edit an existing article,
change that local file; its content fingerprint will cause the vector index to
refresh before the next search.

## Run the offline unit tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

These focused tests cover chunk boundaries/overlap, vector similarity,
filtering weak retrieval matches, the no-context fallback, and HTTP input
validation. They do not call Groq or download the embedding model.

## CORS when using a separate frontend

The included page is served by FastAPI and is same-origin. For a separate local
frontend, configure its exact development origin in `ALLOWED_ORIGINS` in `.env`
(comma-separated). Before deploying a real website, change that list to only
the exact HTTPS website origin, such as `https://support.example.com`, and
remove local origins. CORS controls which browser origins can read responses;
it is not authentication or protection against direct API clients.

## Current tradeoffs

This learning version uses a JSON vector file and in-process indexing, not a
dedicated vector database. Character-based chunking and the 0.68 similarity
cutoff are starter heuristics checked against only a few sample questions, not
measured accuracy claims or guarantees. The app has no
authentication, rate limiting, or multi-user storage, so do not expose it
publicly as-is. See `LEARNING_GUIDE.md` for limitations and next steps.

## Interview topics to prepare

- Trace a question from the FastAPI route through chunk retrieval and model
  generation, then explain the returned source passages.
- Explain why chunk overlap, embeddings, cosine similarity, and source metadata
  are used.
- Explain the fallback threshold and why citations do not guarantee accuracy.
- Explain why the Groq API key is backend-only and how CORS differs from
  authentication.
- Discuss when a JSON index should be replaced by a dedicated vector store.
