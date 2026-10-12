# ITC Treatment Assistant — PlacidWay Assessment Chatbot

A grounded RAG chatbot that answers visitor questions about the ITC Immunity Therapy
Center using **only** content from 7 official PlacidWay pages. Built with **n8n**
(no-code), **Supabase pgvector**, and **Google Gemini** (free tier).

> Design principle: a small, reliable bot that says "I don't know" beats a big,
> impressive-looking one that makes things up.

## Architecture

```
PlacidWay pages (7 URLs)
        │  Workflow 1 "Placidway Ingestion" (run once to refresh)
        ▼
List pages → Fetch page → Clean & chunk (~1200 chars) → Embed chunk (Gemini)
        → Attach embedding → Store in Supabase `placidway_docs` (pgvector)
        (7 nodes, one straight line — n8n runs each step per item, no loops)

Visitor question
        │  Workflow 2 "Placidway Chatbot" (Chat Trigger webhook)
        ▼
Embed question → Retrieve top-5 chunks (match_documents RPC, cosine similarity)
        → Fetch last 6 chat_history rows (follow-up context)
        → Build strict grounding prompt → Ask Gemini 2.0 Flash
        → Format answer (sources + disclaimer appended)
        → Save history → Log event (answered/unanswered + lead email)
        → Reply
        (10 nodes, one straight line — no branches, no loops)
```

**Why this stack:**
- **n8n** — my core tool; every step (ingestion, retrieval, grounding, fallback)
  is visible as a node, which is exactly what the brief asks to see.
- **Plain HTTP nodes, no LangChain magic** — embeddings, vector search, and chat
  are plain REST calls (Gemini API, Supabase REST/RPC). Easier to debug, explain,
  and change live.
- **Supabase pgvector (free tier)** — one SQL function (`match_documents`) does
  cosine-similarity retrieval.
- **Gemini 2.0 Flash (free tier)** — fast, generous free quota, good instruction
  following for the strict grounding prompt. Temperature 0.2 to reduce creativity.

## Setup

1. **Supabase** (free): create a project, run `supabase-setup.sql` in the SQL
   editor. Copy the project URL and anon key.
2. **Gemini API key** (free): Google AI Studio → create key.
3. **n8n**: import `workflows/placidway-ingestion.json` and
   `workflows/placidway-chatbot.json` (⋯ → Import from file).
4. In every HTTP node, replace `YOUR_GEMINI_API_KEY`, `YOUR_SUPABASE_URL`,
   `YOUR_SUPABASE_ANON_KEY` with your values.
5. Run **Placidway Ingestion** once (Manual Trigger) — fills `placidway_docs`.
6. Activate **Placidway Chatbot**, copy the Chat Trigger **Production** webhook URL.
7. Paste the webhook URL into `chat-page/index.html`
   (`PASTE_YOUR_N8N_CHAT_WEBHOOK_URL_HERE`), host the folder on GitHub Pages
   (or any static host) → public demo link.
8. **Refresh**: re-run the ingestion workflow whenever pages change
   (or put it on an n8n Schedule trigger).

## Grounding rules (enforced in the "Build prompt" node)

- Answer ONLY from retrieved excerpts; every answer cites its source URL(s).
- Unknown → exact fallback: *"I don't know the answer to that from the ITC
  pages. Please contact PlacidWay for a free quote."* Never invent prices,
  clinics, or medical facts.
- Prices always with currency + page context (e.g. "starting from $18,995").
- Wrong premise from visitor (e.g. "I heard it costs $50") → politely corrected.
- Booking requests → can't book; point to PlacidWay contact/quote form.
- Out-of-scope (weather etc.) → politely declined.
- Medical advice → no diagnosis; brief disclaimer + "consult your doctor".
- Follow-ups resolved via stored chat history.
- Visitor's language honored (Spanish/Arabic questions answered in kind).
- Quote interest → asks for name/email; emails saved to `chat_events`.
- Every chat logged to `chat_events` as answered/unanswered (content-gap analysis).

## Test results

See `test-results.md` (8 assessment questions run against the live demo).

## What I'd improve with another week / known limitations

See `writeup.md`.

## Files

- `workflows/placidway-ingestion.json` — ingestion workflow (import-ready)
- `workflows/placidway-chatbot.json` — chat workflow (import-ready)
- `supabase-setup.sql` — tables + vector search function
- `chat-page/index.html` — public chat page (GitHub Pages)
- `scrape.py` — reference polite scraper used to validate content extraction
- `test-results.md`, `writeup.md`
