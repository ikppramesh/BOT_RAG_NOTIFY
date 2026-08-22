# RAG Add-On — "Ask Doubt" Feature

## 1. Purpose

The bot today is one-directional: it pushes check-in prompts and records
structured replies. This design adds a second, student-initiated channel —
**`/ask <question>`** — where a student can ask a study question ("What's
in the Polity syllabus for Panchayati Raj?", "Give me 3 PYQs on Federalism",
"What did the mentor say about answer-writing structure?") and the bot
answers by retrieving relevant chunks from mentor-curated material and
generating a grounded response with Claude, instead of guessing from the
model's general knowledge.

This is a distinct system from the check-in workflows and the QuickSight
pipeline (`QUICKSIGHT_DASHBOARD_ARCHITECTURE.md`) — it shares only the same
Telegram bot and n8n instance. It does not touch Google Sheets.

## 2. Scope of the corpus (v1)

Only mentor-supplied material — not the open web, not model memory:

- UPSC syllabus documents (GS papers, optional subjects)
- Previous Year Question banks (PYQs), tagged by subject/year
- Mentor notes / answer-writing guidelines already circulated to students
- FAQ document ("how is productivity scored", "what if I miss a check-in")

Anything not in this corpus should produce "I don't have material on that —
ask your mentor directly," not a generated guess. This matters more here
than in a general chatbot: wrong UPSC facts are actively harmful to exam
prep.

## 3. Two implementation tracks

| | **Track A — Zero-ops (recommended to start)** | **Track B — Fully self-hosted** |
|---|---|---|
| Vector DB | Qdrant Cloud free tier (1 GB, enough for thousands of chunks) | Qdrant OSS via Docker on the same VPS as self-hosted n8n (Option B in `README.md`) |
| Embeddings | Voyage AI API (Anthropic's recommended embeddings partner — pairs naturally with Claude, generous free tier) | Self-hosted embedding microservice (FastAPI + `fastembed`/BGE-small, CPU-only, no GPU needed) |
| Generation | Claude API (already a dependency via `cloud_setup_assistant.py`) | Same |
| Ops burden | None — everything is an HTTP call from n8n | One small Python service to run and monitor alongside n8n |
| Cost | ~free at this scale (few hundred students, low query volume) | Free besides existing VPS |

Start with **Track A**: it needs zero new infrastructure, wires entirely
through n8n's HTTP Request node, and can migrate to Track B later by
swapping two HTTP endpoints (embedding call, Qdrant host) — the collection
schema and n8n workflow shape don't change.

## 4. Architecture

```mermaid
flowchart TB
    subgraph Ingestion["Ingestion (run on-demand, when mentor adds material)"]
        DOC[Mentor uploads PDF/DOCX\nto a Google Drive folder]
        TRG[n8n: Google Drive Trigger\nnew file in folder]
        EXT[Extract text\nPDF/DOCX → plain text]
        CHK[Chunk\n~500 tokens, 50 overlap,\nsplit on headings where possible]
        EMB1[Embed each chunk\nVoyage AI voyage-3-lite]
        UP[Upsert to Qdrant\ncollection: study_material]
    end

    subgraph Query["Query time (new n8n workflow 07_rag_query.json)"]
        TG[Telegram Trigger\nmessage starts with /ask]
        Q[Extract question text]
        EMB2[Embed question\nVoyage AI]
        SRCH[Qdrant search\ntop_k=5, score_threshold]
        GATE{Any chunk above\nscore_threshold?}
        PROMPT[Build grounded prompt\nquestion + retrieved chunks]
        CLAUDE[Claude API\nanswer strictly from context]
        REPLY[Telegram reply\nanswer + source doc names]
        FALLBACK[Telegram reply\n"No material on this —\nask your mentor"]
        LOG[Append to Sheets tab\nRAG Query Log]
    end

    DOC --> TRG --> EXT --> CHK --> EMB1 --> UP
    TG --> Q --> EMB2 --> SRCH --> GATE
    GATE -- yes --> PROMPT --> CLAUDE --> REPLY --> LOG
    GATE -- no --> FALLBACK --> LOG
```

## 5. Ingestion pipeline (new: `07_ingest_material.json`)

Runs whenever a mentor drops a new file, not on a schedule (content changes
rarely — this is unlike the daily check-in exports):

1. **Google Drive Trigger** — watch a shared "Study Material" folder for new files.
2. **Extract text** — n8n's built-in "Extract from File" node handles PDF/DOCX/TXT.
3. **Chunk** — Function node splits into ~500-token windows with ~50-token overlap; prefer splitting on headings/paragraph breaks over hard token cuts so a chunk doesn't cut a PYQ mid-question.
4. **Embed** — HTTP Request to Voyage AI's `/embed` endpoint, batch the chunks.
5. **Upsert** — HTTP Request to Qdrant's `/collections/study_material/points` with each chunk's vector + payload:

```json
{
  "id": "<uuid>",
  "vector": [...],
  "payload": {
    "text": "chunk text",
    "source_doc": "Polity_Syllabus_2026.pdf",
    "subject": "GS2",
    "doc_type": "syllabus",
    "uploaded_at": "2026-08-22"
  }
}
```

`subject` and `doc_type` are filterable metadata — later this lets a query
scope search to just PYQs, or just a student's optional subject.

## 6. Query pipeline (new: `07_rag_query.json`)

1. **Telegram Trigger** — filter to messages matching `/ask ` prefix, so this never collides with workflow 04's check-in reply capture (button taps and free-text morning/evening replies are untouched).
2. **Embed the question** (Voyage AI, same model as ingestion — embedding model must match between corpus and query).
3. **Qdrant search** — `top_k=5`, with a **score threshold**. This is the most important guardrail: below the threshold, there's no good match, and the bot must say so rather than let Claude free-associate.
4. **Prompt construction** (Function node) — strict grounding instruction:

```
Answer the student's question using ONLY the context below. If the context
doesn't contain the answer, say "I don't have material on that — please ask
your mentor directly." Do not use outside knowledge. Cite which document
each fact comes from.

Context:
{{ retrieved chunks with source_doc labels }}

Question: {{ student's question }}
```

5. **Claude API call** — low temperature (favor faithfulness over creativity).
6. **Telegram reply** — answer plus a line like `Source: Polity_Syllabus_2026.pdf`.
7. **Log the query** — append `{date, student_id, question, matched (y/n), source_docs}` to a new **`RAG Query Log`** tab in the same Google Sheet used today. This is deliberately cheap and reuses existing infra rather than adding a new datastore for logs.

## 7. Guardrails specific to exam-prep RAG

- **Score threshold, not just top-k** — an irrelevant top-5 is worse than no answer for exam content.
- **No outside knowledge in the prompt** — explicit instruction, and keep `temperature` low.
- **Always name sources** — lets a student (or mentor, reviewing the log) verify against the original document.
- **Escalation, not silence** — a miss always gets a reply directing the student to their mentor, never a dropped message.
- **Corpus versioning** — when a mentor re-uploads a corrected file, delete the old chunks for that `source_doc` before upserting the new ones (Qdrant `delete` by payload filter on `source_doc`), so stale/incorrect content doesn't linger in search results.

## 8. Ties back to the QuickSight design

The `RAG Query Log` tab is a natural new source for the **Operational
Health** dashboard page already scoped in `QUICKSIGHT_DASHBOARD_ARCHITECTURE.md`
(Section 8, Phase 5): question volume over time, top unanswered topics
(`matched = no`), and which subjects get asked about most — signal for
mentors on where students are stuck, without reading every chat.

## 9. Cost estimate (few hundred students, light `/ask` usage)

| Item | Cost |
|---|---|
| Qdrant Cloud free tier | $0 |
| Voyage AI embeddings | Free tier covers low-volume prep-school usage; pay-as-you-go beyond that, cents per 1K chunks |
| Claude API (generation) | Pay-per-token; a few hundred `/ask` calls/month is low single-digit $ |
| **Total** | **Effectively free at this scale** |

## 10. Rollout

| Phase | Deliverable |
|---|---|
| 1 | Stand up Qdrant Cloud collection + Voyage AI key; manually ingest 3–5 documents to validate chunking/retrieval quality |
| 2 | Build `07_ingest_material.json`, connect the Drive folder |
| 3 | Build `07_rag_query.json`, test `/ask` end-to-end with the pilot group of 5 students (same pilot cohort as `LAYMAN_SETUP_GUIDE.md` Step 9) |
| 4 | Add `RAG Query Log` tab + review cadence for mentors |
| 5 | *(optional)* Migrate to Track B (self-hosted Qdrant + embedding service) if volume or cost outgrows the free tiers |
