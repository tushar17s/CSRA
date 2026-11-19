# Learning Guide: Customer Support RAG Assistant

This guide explains the code in this project as it is built. It uses concrete
examples from the sample support articles rather than assuming prior GenAI
experience.

## 1. Overall architecture and request lifecycle

**Plain language.** A browser sends a question to a Python web server. The
server looks up matching passages in local files, asks a language model to
write an answer from those passages, and returns both the answer and evidence.

**Why it is needed.** A language model does not automatically know the current
support rules in our files. Retrieval finds the relevant rules before answer
generation.

**In this project.** `static/index.html` will call `POST /chat` in
`app/main.py`. The route calls `RagService.answer_question` in `app/rag.py`.
That method refreshes the local vector index, embeds the question, selects
similar passages, and—only when there is a good match—calls Groq for a draft.
The response contains the answer, source filenames, and matching passages.

**Analogy.** This is like asking a support agent to search the team handbook
before replying, then attaching the handbook paragraphs used.

**Support example.** For “How long does a password reset link last?”, the
assistant can retrieve `account_access.md` and draft a reply from its 30-minute
expiry rule.

**What can go wrong.** If the question is vague, the best available passages may
still be a poor match. `select_relevant_passages` uses a similarity cutoff and
returns no passages when every match is weak; then `answer_question` returns a
fixed fallback instead of calling the model.

**Interview summary.** “The API embeds a question, retrieves relevant local
chunks by cosine similarity, and gives only those chunks to the generation
model. It returns citations as filenames and passages.”

## 2. HTTP, FastAPI routes, request/response models, and CORS

**Plain language.** HTTP is the request-and-response format browsers and
servers use. A route maps a method and URL, such as `POST /chat`, to Python
code. Request/response models describe the JSON shape.

**Why it is needed.** The browser needs a predictable contract with the Python
backend, and invalid input should be rejected before it reaches retrieval.

**In this project.** `app/main.py` defines `GET /health`, `POST /documents`,
and `POST /chat`. `app/models.py` defines `ChatRequest`, `ChatResponse`,
`RetrievedPassage`, and `DocumentUploadResponse`. Pydantic checks that the
question is non-empty and no longer than 2,000 characters, and FastAPI formats
the response models as JSON. The upload route limits documents to 1 MB and
accepts only UTF-8 `.txt` and `.md` files.

The `CORSMiddleware` setup in `app/main.py` allows the two local development
origins listed in `ALLOWED_ORIGINS`; it allows only `GET` and `POST` and does
not allow browser credentials. The included page is served by FastAPI at `/`,
so it is same-origin and does not need CORS. CORS is useful if you later run a
separate local frontend. Before publishing a real website, set
`ALLOWED_ORIGINS` to only its exact HTTPS origin (for example
`https://support.example.com`) and remove local origins. CORS is a browser
access rule, not user authentication.

**Analogy.** Routes are service-desk counters with labels; request models are
the forms each counter accepts.

**Support example.** The chat form sends `{"question":"Where can I download my invoice?"}`.
The response contract includes an `answer`, a list of `sources`, and a list of
`passages`.

**What can go wrong.** Missing questions, unsupported file extensions, invalid
UTF-8, oversized files, or duplicate filenames receive understandable HTTP
errors. An unavailable Groq key is reported as `503`; a failed provider call
as `502`. `ChatRequest` trims the question and rejects whitespace-only input.

**Interview summary.** “FastAPI declares typed route contracts, validates the
input with Pydantic, and uses narrowly scoped CORS for local development.”

## 3. Environment variables and backend-only API keys

**Plain language.** Environment variables configure an app without hard-coding
machine-specific values or secrets in source code.

**Why it is needed.** A Groq API key authorizes billable model requests. If it
were included in browser JavaScript, every visitor could inspect and reuse it.

**In this project.** `app/config.py` loads the root `.env` using
`python-dotenv`; `app/rag.py` reads `GROQ_API_KEY` on the server when it needs
to create the Groq client. The browser never receives the key. `.env.example`
shows variable names and safe placeholders. `.gitignore` excludes `.env`.
`MODEL_NAME` selects the generation model, while `ALLOWED_ORIGINS` configures
local browser origins.

**Analogy.** The API key is a staff-only keycard; the browser can ask the server
to do a task, but never gets to carry the keycard.

**Support example.** A support operator puts their own key in the local `.env`;
the chat page sends only a question to `/chat`, not the key.

**What can go wrong.** If `GROQ_API_KEY` is missing, answer generation is
explicitly rejected with a configuration message. Never replace `.env` with
`.env.example` containing a real key, and never paste keys into HTML or Python
source.

**Interview summary.** “Secrets are loaded by backend configuration from an
ignored `.env`; browser code calls our API and never sees the provider key.”

## 4. Knowledge-base documents and ingestion

**Plain language.** The knowledge base is a set of small text articles, each
about one support subject. Ingestion is the process of turning those files
into searchable chunks and vectors.

**Why it is needed.** Focused articles are easier for a retriever to match and
easier for a support team to update than one large, mixed document.

**In this project.** `knowledge_base/` starts with five Markdown articles:
account access, billing and invoices, cancellations and refunds, shipping,
and returns. `POST /documents` in `app/main.py` validates and saves another
`.txt` or `.md` file. `RagService._refresh_index` in `app/rag.py` reads files,
checks a SHA-256 content fingerprint, and embeds only added or changed
documents. Deleted documents are removed from the saved index. A duplicate
filename is rejected instead of silently overwriting an article.

**Analogy.** Each article is a labeled binder in a support library; ingestion
creates index cards for the pages so they can be found quickly.

**Support example.** Add a `warranty.md` article with a unique filename; it is
embedded automatically before the next chat search.

**What can go wrong.** Unsupported formats, empty files, malformed UTF-8,
duplicate names, and files over 1 MB are rejected. The index refresh is
content-based, so editing an existing article triggers new vectors on the next
search.

**Interview summary.** “The upload endpoint validates and persists plain
documents, and the RAG service syncs changed files into the vector store using
content hashes.”

## 5. Chunking and overlap

**Plain language.** Chunking splits long articles into smaller passages so
search can return the specific section relevant to a question. Overlap repeats
a small portion at the edge of adjacent chunks.

**Why it is needed.** Sending whole files can bury an answer in unrelated text;
splitting at an arbitrary boundary can separate a rule from its context.

**In this project.** `chunk_text` in `app/rag.py` makes chunks of at most 800
characters with a 120-character overlap. The helper validates its size
settings and skips blank input. It uses character windows to stay easy to
understand; it does not yet split on sentence or token boundaries.

**Analogy.** It is like photocopying a long manual in overlapping page ranges,
so a sentence at the bottom of one page is still visible on the next.

**Support example.** If a return-policy sentence falls at the end of one
chunk, some of its wording is repeated in the next chunk.

**What can go wrong.** Too-small chunks lose context; too-large chunks include
unrelated detail. Overlap duplicates some text, trading a little extra storage
for more complete context.

**Interview summary.** “We use fixed character windows with a small overlap as
a transparent first chunking strategy; token-aware or structure-aware
chunking is a reasonable improvement.”

## 6. Embeddings, vector search, and stored metadata

**Plain language.** An embedding is a list of numbers that represents a piece
of text. Texts with related meaning tend to have vectors pointing in similar
directions. Vector search compares the question vector with passage vectors.

**Why it is needed.** A keyword-only search may miss that “reset my login
secret” is related to an article about “password resets.” Embeddings can match
meaning rather than requiring identical words.

**In this project.** `RagService._get_embedding_model` loads
`BAAI/bge-small-en-v1.5` through FastEmbed on the backend, and `_embed_texts`
converts its vectors to ordinary Python floats. `cosine_similarity` compares
vectors; `retrieve` ranks chunks and `select_relevant_passages` keeps up to
three with similarity at least `0.68`. `data/vector_store.json` stores each
chunk's `source`, `text`, and numeric `embedding`, plus file fingerprints.
The JSON index is generated locally and ignored by Git.

**Analogy.** Each passage has a coordinate on a map of meaning; cosine
similarity finds the nearby map points for the question.

**Support example.** A question about a “monthly charge date” may retrieve a
billing article that uses the phrase “subscription renews,” even when the exact
words differ.

**What can go wrong.** An embedding model can rank a plausible but irrelevant
passage, and similarity thresholds are not universal. The `0.68` cutoff is a
starter heuristic selected after checking a few sample questions against this
small article set; it is not an accuracy score or a guarantee. Tune it using
representative questions and human-reviewed retrieval results. The first local
embedding call downloads the model, and a corrupt vector JSON file needs to be
removed and rebuilt.

**Interview summary.** “We store dense passage vectors with their source
metadata, rank by cosine similarity, and return source names so retrieval is
inspectable and answers are attributable.”

## 7. RAG flow, prompt grounding, and fallback

**Plain language.** Retrieval-augmented generation (RAG) finds relevant
external text first, then gives that text to a language model to draft a
response.

**Why it is needed.** The model should answer support-policy questions from the
team's current articles rather than relying on its general training data.

**In this project.** `RagService.answer_question` calls `retrieve`, formats
the top passages with `[Source: filename]`, and sends them to Groq with a
system instruction to use only the supplied passages, treat their content as
reference rather than instructions, avoid invented policy details, and mention
source filenames. If retrieval returns no match above the threshold, the
service returns `FALLBACK_ANSWER` without calling Groq. Every successful chat
response also includes the exact retrieved passage text and source filename.

**Analogy.** The model is a writer who may only answer after receiving the
relevant pages from a reference binder; if the binder has no answer, the writer
must say so.

**Support example.** The cancellation article says access continues through
the paid billing period but does not state every refund exception. The prompt
instructs the model not to invent an exception or timeline.

**What can go wrong.** Prompt instructions reduce unsupported answers but
cannot guarantee perfect behavior. A wrong retrieval can still provide the
wrong context; the cited passages let a human inspect that context. The fixed
fallback is used only when the similarity cutoff filters out all passages.

**Interview summary.** “RAG grounds a generation call in retrieved passages;
we set explicit source-only instructions, return evidence, and skip generation
when no passage clears the retrieval threshold.”

## 8. Browser communication and the full request lifecycle

**Plain language.** The browser sends ordinary HTTP requests to FastAPI and
renders the JSON responses. It does not compute embeddings or contact Groq.

**Why it is needed.** Keeping the retrieval and provider calls in Python keeps
the API key private and lets the browser stay a small, replaceable interface.

**In this project.** `static/index.html` is served at `/` by the `home`
function in `app/main.py`. Its chat form uses `fetch("/chat", ...)` with JSON
containing the question. It reads the response, displays the answer, and
creates source cards showing each filename, similarity, and passage. The
upload form sends a `FormData` file to `/documents`; it does not set the
multipart content type itself because the browser must add the boundary.
Rendering uses `textContent` and DOM element creation rather than inserting
untrusted response text as HTML.

The lifecycle is: (1) the person submits a question; (2) the page sends JSON to
FastAPI; (3) `ChatRequest` validates it; (4) `RagService` notices changed local
files and embeds them if needed; (5) the question is embedded and compared
against stored vectors; (6) either the fallback is returned or the selected
passages are sent to Groq; (7) `ChatResponse` returns the answer and evidence;
(8) the browser renders all returned text safely.

**Analogy.** The browser is the support desk's request form and results screen;
the Python backend is the private filing room and the staff member who drafts
the response.

**Support example.** After a support agent uploads a new shipping article in
the page, the next shipping question triggers indexing and shows the new
article's filename and matching passage in the result.

**What can go wrong.** Network errors and API errors are displayed in a status
area rather than silently discarded. If running a frontend on a separate
origin, configure that exact origin in backend CORS settings. Never put the
Groq key in a page script.

**Interview summary.** “The UI calls same-origin FastAPI endpoints with
`fetch`, renders backend citations, and never handles provider credentials.”

## 9. Current limitations and sensible next improvements

- The vector store is a small local JSON file and is suitable for learning, not
  for concurrent multi-user production traffic.
- Character chunking and the similarity cutoff are simple heuristics. A next
  step is to evaluate a set of real, privacy-safe support questions and
  hand-check retrieval before adjusting chunk size or cutoff.
- The Groq answer can still make mistakes; review citations and passages.
- The embedding model downloads on first use, so that first request needs
  network access.
- There is no authentication or per-user authorization. Do not expose this
  local upload endpoint publicly without adding appropriate access controls.

For an interview, be ready to walk through one `/chat` request from the browser
to the retrieved source passage, describe where vectors and filenames are
stored, and explain why the fallback and citations matter. The exact local
commands are in `README.md`.
