# Write-up: what I'd improve with another week, and known limitations

## Improvements (one more week)
1. **Better chunking** — switch from fixed ~700-char chunks to section-aware
   splitting (headings as boundaries), so package "includes" lists never get
   cut mid-list.
2. **Hybrid retrieval** — combine vector similarity with keyword matching
   (e.g. exact price figures), because pure embeddings sometimes miss a
   "$18,995" sitting in a chunk whose wording differs from the question.
3. **Evaluation harness** — a scripted set of 30+ questions (paraphrases, tricky
   premises, other languages) run automatically after every prompt change, so
   grounding regressions get caught before deployment.
4. **Smarter refresh** — hash page content and only re-embed changed sections
   instead of the full re-ingest.
5. **Richer lead capture** — conversational name + treatment-interest capture,
   not just email regex, stored against the session.

## Known limitations
- **Embedding quality ceiling**: text-embedding-004 is good but not perfect;
  very short or ambiguous questions can retrieve a weakly related chunk. The
  strict prompt + "I don't know" fallback is the safety net, not the retriever.
- **No live price verification**: prices are only as fresh as the last ingestion
  run. If PlacidWay edits a price, the bot is stale until refresh.
- **Single-clinic scope**: the bot knows only the 7 ITC pages. Comparisons like
  "cheaper in Turkey?" correctly get "I don't know" — by design, but a real
  product would need broader coverage.
- **Free-tier quotas**: Gemini free tier and Supabase free tier are enough for
  assessment traffic, not for production scale.
- **Session memory is short**: only the last 6 exchanges are kept, so very long
  conversations lose early context.
