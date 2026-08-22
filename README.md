# BOT_RAG_NOTIFY

**Automated daily accountability and notification system for UPSC mentorship programs.**

A Telegram bot automation built on [n8n](https://n8n.io) that sends scheduled check-in messages to students, captures their responses via inline keyboard buttons, stores data in Google Sheets, and delivers weekly performance summaries — all without any manual intervention.

Originally designed for **LA Excellence IAS Academy** to track study progress across 80+ UPSC aspirants.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Setup](#quick-setup)
- [Manual Setup](#manual-setup)
- [Google Sheet Schema](#google-sheet-schema)
- [Credential Reference](#credential-reference)
- [Running Locally](#running-locally)
- [Deployment Options](#deployment-options)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Overview

BOT_RAG_NOTIFY automates three core daily touchpoints with students:

| Time | Action |
|------|--------|
| 7:00 AM IST | Morning check-in — students set their study target for the day |
| 2:00 PM IST | Afternoon motivational nudge |
| 9:30 PM IST | Evening check-in — 5 quick button-tap questions on progress |

Responses are captured in real time and written to a shared Google Sheet. Every Sunday at 10:00 AM, each student receives a personalised weekly performance summary.

---

## Architecture

```
Telegram Bot (@Irmentor_bot)
        │
        ▼
   ngrok tunnel  ◄──── local/cloud n8n instance
        │
        ▼
   n8n Workflows (5 automations)
        │
        ├──► Google Sheets  (student registry + daily responses)
        └──► Telegram API   (outbound messages & inline keyboards)
```

**Components:**

| Component | Technology |
|-----------|-----------|
| Bot platform | Telegram Bot API |
| Automation engine | n8n (self-hosted or n8n Cloud) |
| Data storage | Google Sheets |
| Webhook tunnel (local) | ngrok |
| Setup automation | Python 3 + Anthropic Claude API |

---

## Workflows

Five n8n workflow files live in `n8n_workflows/`:

| File | Purpose | Schedule |
|------|---------|----------|
| `01_morning_checkin.json` | Sends morning study-target question to all students | 7:00 AM IST daily |
| `02_afternoon_nudge.json` | Sends motivational message | 2:00 PM IST daily |
| `03_night_checkin.json` | Sends 5 button-tap progress questions | 9:30 PM IST daily |
| `04_capture_replies.json` | Listens for student messages & button taps; writes to Google Sheets | Always-on (24/7) |
| `05_weekly_summary.json` | Calculates and sends personalised weekly report | Sunday 10:00 AM IST |

### Activation Order

Import and activate **`04_capture_replies.json` first** (the webhook listener must be live before the outbound workflows run).

```
04 → 01 → 02 → 03 → 05
```

### Inline Button Callback Data

The evening check-in workflow (`03_night_checkin.json`) sends inline keyboard buttons. Workflow 04 maps the `callback_data` values to Google Sheet columns:

```
Hours studied : hours_lt4 | hours_4to6 | hours_6to8 | hours_8plus
Subjects      : subj_gs   | subj_optional | subj_both | subj_revision
Test today?   : test_yes  | test_no
Productivity  : prod_1 | prod_2 | prod_3 | prod_4 | prod_5
Day status    : status_full | status_partial | status_notdone
```

---

## Project Structure

```
BOT_RAG_NOTIFY/
├── n8n_workflows/
│   ├── 01_morning_checkin.json      # 7 AM morning check-in workflow
│   ├── 02_afternoon_nudge.json      # 2 PM afternoon nudge workflow
│   ├── 03_night_checkin.json        # 9:30 PM evening check-in workflow
│   ├── 04_capture_replies.json      # Always-on reply capture workflow
│   ├── 05_weekly_summary.json       # Weekly summary workflow
│   └── README.md                    # Workflow-specific notes
├── cloud_setup_assistant.py         # AI-guided setup automation (uses Claude API)
├── fix_webhook.py                   # Re-point Telegram webhook to current ngrok URL
├── start_n8n.sh                     # Start local n8n with ngrok webhook config
├── cred.env.example                 # Credential template (copy to cred.env, fill in values)
├── SETUP_GUIDE.md                   # Technical step-by-step setup guide
├── LAYMAN_SETUP_GUIDE.md            # Non-technical setup guide (no coding required)
├── PRD_LA_Excellence_Mentorship_Automation.md  # Full product specification
├── QUICKSIGHT_DASHBOARD_ARCHITECTURE.md  # Data architecture for a QuickSight mentor dashboard
├── RAG_ARCHITECTURE.md               # RAG "/ask" add-on: vector DB, ingestion & query design
└── README.md
```

---

## Prerequisites

- **n8n** — self-hosted (`npm install -g n8n`) or [n8n Cloud](https://n8n.io/cloud/)
- **ngrok** — for local webhook tunnelling (`brew install ngrok/ngrok/ngrok`)
- **Python 3.8+** — for the setup automation scripts
- **Telegram Bot token** — create a bot via [@BotFather](https://t.me/BotFather)
- **Google Sheets** — a Google account with Sheets API access enabled
- **Anthropic API key** (optional) — only needed for the AI-guided `cloud_setup_assistant.py`

---

## Quick Setup

The fastest path uses the AI-guided setup assistant:

```bash
# 1. Clone the repo
git clone https://github.com/ikppramesh/BOT_RAG_NOTIFY.git
cd BOT_RAG_NOTIFY

# 2. Copy and fill in your credentials
cp cred.env.example cred.env
# Edit cred.env with your Telegram bot token, Google Sheet ID, etc.

# 3. Install the only Python dependency
pip install anthropic

# 4. Set your Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 5. Run the assistant — it will import workflows, connect credentials, and activate everything
python3 cloud_setup_assistant.py
```

The assistant will prompt you for your n8n instance URL and API key, then do the rest automatically.

---

## Manual Setup

### Step 1 — Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram.
2. Send `/newbot` and follow the prompts.
3. Copy the **bot token** (format: `123456789:ABCdef...`).

### Step 2 — Create the Google Sheet

Create a new Google Sheet with two tabs:

**Tab: Student Registry**

| student_name | telegram_chat_id | batch_group | start_date | optional_subject |
|---|---|---|---|---|

**Tab: Daily Responses**

| Date | Student Name | Telegram Chat ID | Morning Target | Planned Subjects | Planned Hours | Evening Status | Hours Completed | Hours Label | Subjects Covered | Test Written Today? | Productivity (1-5) | Blockers/Notes | Timestamp |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Copy the Google Sheet ID from its URL:
`https://docs.google.com/spreadsheets/d/**<SHEET_ID>**/edit`

### Step 3 — Configure n8n Credentials

In your n8n instance:
1. Go to **Credentials → New**.
2. Add a **Telegram API** credential with your bot token.
3. Add a **Google Sheets OAuth2** credential and authorise your Google account.

### Step 4 — Import Workflows

Import the JSON files via **n8n → Workflows → Import from file**, in this order:

```
04_capture_replies.json  ← import & activate first
01_morning_checkin.json
02_afternoon_nudge.json
03_night_checkin.json
05_weekly_summary.json
```

After importing each workflow, open it and re-assign the Telegram and Google Sheets credentials in each node that uses them.

### Step 5 — Set the Telegram Webhook

For **local n8n with ngrok**:

```bash
# Start n8n (edit NGROK_URL in start_n8n.sh first)
chmod +x start_n8n.sh
./start_n8n.sh

# In a second terminal, start ngrok
ngrok http 5678

# Point Telegram's webhook to your ngrok URL
python3 fix_webhook.py
```

For **n8n Cloud**, the webhook URL is provided automatically by n8n — just activate workflow 04 and Telegram will route updates there.

---

## Google Sheet Schema

### Student Registry tab

| Column | Type | Description |
|--------|------|-------------|
| `student_name` | Text | Full name of the student |
| `telegram_chat_id` | Number | Telegram chat ID (obtained by messaging the bot) |
| `batch_group` | Text | Batch identifier (e.g., "Batch A") |
| `start_date` | Date | Date the student enrolled |
| `optional_subject` | Text | UPSC optional paper subject |

### Daily Responses tab

| Column | Description |
|--------|-------------|
| `Date` | Response date (YYYY-MM-DD) |
| `Student Name` | Pulled from Student Registry |
| `Telegram Chat ID` | Student's chat ID |
| `Morning Target` | Free-text target set in the morning |
| `Planned Subjects` | Subjects planned for the day |
| `Planned Hours` | Hours planned |
| `Evening Status` | `status_full` / `status_partial` / `status_notdone` |
| `Hours Completed` | `hours_lt4` / `hours_4to6` / `hours_6to8` / `hours_8plus` |
| `Hours Label` | Human-readable label (e.g., "6–8 hours") |
| `Subjects Covered` | `subj_gs` / `subj_optional` / `subj_both` / `subj_revision` |
| `Test Written Today?` | `test_yes` / `test_no` |
| `Productivity (1-5)` | Self-rated score from 1 to 5 |
| `Blockers/Notes` | Optional free-text note |
| `Timestamp` | ISO timestamp of when the response was recorded |

---

## Credential Reference

Copy `cred.env.example` to `cred.env` and fill in:

```env
# Telegram Bot
BOT_TOKEN=<your_telegram_bot_token>

# Google Sheets
SHEET_ID=<your_google_sheet_id>

# n8n (for cloud_setup_assistant.py)
N8N_BASE_URL=https://your-instance.app.n8n.cloud
N8N_API_KEY=<your_n8n_api_key>

# Anthropic (optional — for cloud_setup_assistant.py)
ANTHROPIC_API_KEY=sk-ant-...
```

> **Never commit `cred.env` to version control.** It is listed in `.gitignore`.

---

## Running Locally

```bash
# 1. Start ngrok in one terminal
ngrok http 5678

# 2. Edit start_n8n.sh — replace NGROK_URL with the URL from step 1
#    Then start n8n in another terminal
./start_n8n.sh

# 3. If the ngrok URL changed, re-point the Telegram webhook
python3 fix_webhook.py
```

n8n editor is available at `http://localhost:5678`.

---

## Deployment Options

### Option A — n8n Cloud (recommended)

1. Sign up at [n8n.io/cloud](https://n8n.io/cloud).
2. Use `cloud_setup_assistant.py` to import all workflows automatically.
3. No ngrok needed — n8n Cloud provides the webhook URL.

**Pricing:** Free tier supports ~40 workflow executions/day (~40 students). The Starter plan ($20/month) handles 80+ students.

### Option B — Self-hosted (VPS/Raspberry Pi)

1. Install n8n on a server with a public IP.
2. Use a reverse proxy (nginx + Let's Encrypt) for HTTPS.
3. Set `WEBHOOK_URL` to your public HTTPS URL.
4. Import workflows and activate.

### Option C — Local Mac (development/testing)

Follow the [Running Locally](#running-locally) steps above. Requires ngrok to stay running continuously; the free ngrok tier changes the public URL on restart, so `fix_webhook.py` must be re-run each time.

---

## Troubleshooting

**Workflow 04 shows "no webhook registered"**
- Make sure the workflow is **active** (green toggle in n8n).
- Verify `WEBHOOK_URL` in n8n matches your current ngrok/cloud URL.
- Run `python3 fix_webhook.py` to re-register.

**Students not receiving messages**
- Confirm `telegram_chat_id` values in the Student Registry tab are correct (numeric IDs, not usernames).
- Check the workflow execution logs in n8n for errors.
- Make sure the student has started the bot (`/start`).

**Google Sheets not updating**
- Re-authorize the Google Sheets credential in n8n.
- Ensure the Sheet ID in the workflow nodes matches your sheet.
- Column names in the sheet must match exactly (case-sensitive).

**ngrok URL changed after restart**
- Edit `start_n8n.sh` with the new ngrok URL.
- Restart n8n, then run `python3 fix_webhook.py`.

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/my-change`.
3. Commit your changes: `git commit -m "add: my change"`.
4. Push and open a PR.

---

## License

MIT
