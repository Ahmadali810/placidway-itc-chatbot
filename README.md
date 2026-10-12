# ITC Treatment Assistant — PlacidWay Assessment Chatbot

A grounded RAG chatbot that answers visitor questions about the ITC Immunity Therapy
Center using **only** content from 7 official PlacidWay pages. Built with **n8n**
(AI Agent + Tools), **Pinecone** (vector store), and **OpenAI** (chat + embeddings).

> Design principle: a small, reliable bot that says "I don't know" beats a big,
> impressive-looking one that makes things up.

## Architecture

```
7 PlacidWay pages (PDF)
        │  Indexing flow: "On form submission" (n8n Form Trigger, file upload)
        ▼
Default Data Loader → OpenAI embeddings → Pinecone index "placidway" (namespace "Rag")

Visitor question
        │  Chat flow: "When chat message received" (Chat Trigger, public webhook)
        ▼
AI Agent (Tools Agent, gpt-4o-mini)
   ├── Chat model: OpenAI gpt-4o-mini (Anthropic Claude Haiku 4.5 attached as fallback)
   ├── Memory: Simple Memory (buffer window — resolves follow-ups like "what about recovery time?")
   └── Tool: "Placidway Chatbot" (Pinecone vector store, retrieve-as-tool, topK 5)
        └── Embeddings: OpenAI embeddings
        ▼
Strict system prompt enforces grounding → answer returned by the webhook
```

**Why this stack:**
- **n8n AI Agent** — the Tools Agent pattern keeps retrieval explicit: the agent
  must call the Pinecone tool before answering factual questions, and a strict
  system prompt forbids inventing prices, clinics, or medical facts.
- **Pinecone (free tier)** — managed vector store; one index (`placidway`,
  namespace `Rag`), top-5 retrieval per question.
- **OpenAI** — gpt-4o-mini for chat (fast, cheap, good instruction following),
  OpenAI embeddings for the vector store. Temperature left default; grounding
  comes from the system prompt + tool-only facts.
- **Simple Memory** — short conversation window so follow-up questions resolve
  against what was just discussed.

## Setup

1. **Pinecone** (free): create index `placidway`, note the API key.
2. **OpenAI** API key with access to gpt-4o-mini + embeddings.
3. **n8n**: import `workflows/placidway-chatbot.json`
   (⋯ → Import from file). Connect your Pinecone and OpenAI credentials.
4. **Index the knowledge**: open the form trigger ("On form submission"),
   upload the 7-page source PDF (`Placidway-ITC-7-Pages.pdf`), run once.
   This fills the Pinecone index. Re-upload to refresh.
5. Activate the workflow, copy the Chat Trigger **Production** webhook URL.
6. Paste the webhook URL into `docs/index.html` (`WEBHOOK_URL`),
   push to GitHub, enable GitHub Pages on `docs/` → public demo link.

## Grounding rules (enforced in the AI Agent system prompt)

- Answer ONLY from retrieved Pinecone excerpts; never from training data.
- Unknown → exact fallback: *"I'm sorry, but I couldn't find verified information
  about this in the available PlacidWay knowledge base. Please contact PlacidWay
  directly for accurate information."*
- Prices always with currency + page context (e.g. "$18,995 USD, out-patient, 3 weeks").
- Wrong premise from visitor (e.g. "I heard it costs $50") → never agree; correct politely.
- Booking requests → can't book; point to PlacidWay contact/quote form.
- Out-of-scope (weather etc.) → politely declined.
- Medical advice → no diagnosis; recommend a healthcare professional.
- Follow-ups resolved via Simple Memory.
- Visitor's language honored where possible.
- Greetings answered naturally without a retrieval call.

## Test results

See `test-results.md` — 8 assessment questions run against the live bot
(5 pass, 2 partial, 0 fail).

## Known limitations / improvements

See `writeup.md`.

## Files

- `workflows/placidway-chatbot.json` — the full n8n workflow (chat flow + indexing flow)
- `docs/index.html` — public chat demo page (GitHub Pages)
- `Placidway-ITC-7-Pages.pdf` — source-of-truth: full text of the 7 allowed pages
- `test-results.md` — 8 required test questions with verdicts
- `writeup.md` — architecture notes and improvement ideas
- `pages.json`, `scrape.py` — reference scraper used to validate content extraction
