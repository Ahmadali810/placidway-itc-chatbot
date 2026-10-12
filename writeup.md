# Write-up: what I'd improve with another week, and known limitations

## Improvements (one more week)
1. **Better chunking** — switch from default document splitting to section-aware
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
5. **Richer lead capture** — conversational name + treatment-interest capture
   stored against the session, not just answering questions.

## Known limitations
- **Embedding quality ceiling**: OpenAI embeddings are good but not perfect;
  very short or ambiguous questions can retrieve a weakly related chunk. The
  strict system prompt + "I don't know" fallback is the safety net, not the retriever.
- **No live price verification**: prices are only as fresh as the last indexing
  run. If PlacidWay edits a price, the bot is stale until refresh.
- **Single-clinic scope**: the bot knows only the 7 ITC pages. Comparisons like
  "cheaper in Turkey?" correctly get "I don't know" — by design, but a real
  product would need broader coverage.
- **Free-tier quotas**: Pinecone free tier and OpenAI API usage are enough for
  assessment traffic, not for production scale.
- **Session memory is short**: Simple Memory keeps a small recent window, so very
  long conversations lose early context.
- **Test gaps found 2026-10-13**: country-comparison answers can leak general
  model knowledge (USA price range), and false premises get a soft deflection
  instead of an explicit correction with the verified price. Both are prompt-level
  fixes.
