# n8n Workflow Files — LA Excellence Mentorship Bot

Import these 4 JSON files into n8n in order. See `SETUP_GUIDE.md` (one folder up) for full instructions.

## Files

| File | Workflow | Schedule |
|---|---|---|
| `01_morning_checkin.json` | Sends morning study-target question to all students | 7:00 AM IST daily |
| `02_evening_checkin.json` | Sends 5 button-tap questions for evening progress report | 9:00 PM IST daily |
| `03_capture_replies.json` | Listens for all student replies & saves to Google Sheet | Always-on (24/7) |
| `04_weekly_summary.json` | Calculates and sends a personalized weekly report | Sunday 10:00 AM IST |

## Before Importing — Required Edits

The Spreadsheet ID is already filled in all JSON files:
```
1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs
```

The only thing left to do after importing is connect your credentials inside n8n:
- `YOUR_TELEGRAM_CREDENTIAL_ID` → auto-set when you pick "Telegram API" from the credential dropdown
- `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` → auto-set when you pick "Google Sheets account" from the dropdown

## Import Order

Import in this order: 03 first (always-on listener), then 01, 02, 04.

Activate 03 first. Then activate 01, 02, 04.

## Callback Data Reference

Evening button taps send these `callback_data` values, which workflow 03 parses:

```
Hours:      hours_lt4 | hours_4to6 | hours_6to8 | hours_8plus
Subjects:   subj_gs | subj_optional | subj_both | subj_revision
Test:       test_yes | test_no
Productivity: prod_1 | prod_2 | prod_3 | prod_4 | prod_5
Status:     status_full | status_partial | status_notdone
```

## Google Sheet Column Names (must match exactly)

**Student Registry tab:** `student_name`, `telegram_chat_id`, `batch_group`, `start_date`, `optional_subject`

**Daily Responses tab:** `Date`, `Student Name`, `Telegram Chat ID`, `Morning Target`, `Planned Subjects`, `Planned Hours`, `Evening Status`, `Hours Completed`, `Hours Label`, `Subjects Covered`, `Test Written Today?`, `Productivity (1-5)`, `Blockers/Notes`, `Timestamp`

---

## RAG "/ask" Add-on — `07_ingest_material.json` + `07_rag_query.json`

Design doc: `../RAG_ARCHITECTURE.md`. These two files implement the `/ask <question>`
Telegram command backed by a Qdrant vector DB, Voyage AI embeddings, and Claude —
grounded strictly in mentor-supplied study material and RSS/news current-affairs
feeds, never open-web/model knowledge.

**These node types (Google Drive REST calls, RSS Feed Read, Execute Workflow,
the native Telegram node) are new to this repo** — the 01–05 workflows were
exported directly from a working n8n instance, but 07 was hand-authored against
n8n's node conventions. Import both, open every node once, and fix anything
n8n's editor flags in red before activating.

### New Google Sheet tabs to create

| Tab | Columns |
|---|---|
| `Ingested Files Log` | `file_id`, `file_name`, `ingested_at` |
| `RSS Ingested Log` | `guid`, `ingested_at` |
| `RAG Query Log` | `Date`, `Telegram Chat ID`, `Question`, `Matched`, `Source Docs`, `Timestamp` |

### New credentials to add in n8n (Settings → Credentials → Add Credential)

| Credential | Type | Value |
|---|---|---|
| Google Drive account | Google Drive OAuth2 | authorize the account holding your study-material folder |
| Voyage AI API (Header Auth) | Header Auth | Header name `Authorization`, value `Bearer <your Voyage AI key>` |
| Qdrant API (Header Auth) | Header Auth | Header name `api-key`, value `<your Qdrant API key>` |
| Anthropic API (Header Auth, x-api-key) | Header Auth | Header name `x-api-key`, value `<your Anthropic API key>` |

After adding each, re-assign it in every node that references it (same as the
Telegram/Google Sheets credentials for workflows 01–05).

### One-time manual setup (not automated by these workflows)

1. Create the Qdrant collection before the first ingest run — the workflow
   never creates or recreates it, so a re-run can't accidentally wipe data:
   ```bash
   curl -X PUT "https://YOUR-QDRANT-HOST/collections/study_material" \
     -H "api-key: YOUR_QDRANT_KEY" -H "Content-Type: application/json" \
     -d '{"vectors": {"size": 512, "distance": "Cosine"}}'
   ```
   (512 = `voyage-3-lite`'s embedding dimension.)
2. In both `07_ingest_material.json` nodes named `Upsert Point To Qdrant (...)`
   and in `07_rag_query.json`'s `Search Qdrant — study_material` node, replace
   `REPLACE_WITH_QDRANT_HOST` with your actual Qdrant Cloud/self-hosted host.
3. In `07_ingest_material.json`'s `List Files In Study Material Folder` node,
   replace `REPLACE_WITH_DRIVE_FOLDER_ID` with the Google Drive folder ID
   where mentors will upload PDFs.
4. Edit the `RSS Feed List` node in `07_ingest_material.json` — it ships with
   one example feed; add/replace with the current-affairs sources relevant to
   your syllabus.
5. Import `07_rag_query.json` first, open it, copy its workflow ID from the
   n8n URL bar, and paste it into `04_capture_replies.json`'s
   `Call RAG Query Workflow (07)` node (replacing
   `REPLACE_WITH_07_RAG_QUERY_WORKFLOW_ID`) — n8n workflow IDs are assigned on
   import, so this link can't be pre-filled.

### Activation order

`07_rag_query.json` (sub-workflow, no trigger of its own besides Execute
Workflow) → re-save `04_capture_replies.json` with the ID from step 5 above →
`07_ingest_material.json` (runs on its own 6-hourly schedule).

`07_rag_query.json` intentionally has **no Telegram Trigger of its own** — a
bot can only have one webhook, already owned by `04`'s trigger. It's invoked
as a sub-workflow when `04` detects a message starting with `/ask`.
