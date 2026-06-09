# LA Excellence Mentorship Bot — Complete Setup Guide
### (For non-technical users — follow every step exactly)

---

## What This Bot Does

Once set up, this bot will automatically:
- **7:00 AM every day** → Ask each student: "How many study slots are you targeting today?"
- **2:00 PM every day** → Send a motivational nudge with a daily tip
- **9:30 PM every day** → Ask: "Did you hit your targets?" + log hours + productivity score
- **Every student reply** → Captured and saved to Google Sheet automatically
- **Every Sunday 10 AM** → Send each student a weekly performance summary

---

## What You Need Before Starting

Collect these 4 things. Keep them in a notepad.

| Item | What it is | You already have it? |
|------|-----------|----------------------|
| **Telegram Bot Token** | Looks like: `8711874086:AAG...` | ✅ Yes — `@Irmentor_bot` |
| **Google Sheet ID** | The long ID in your sheet's URL | ✅ Yes — `1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs` |
| **Google Account** | Gmail account that owns the sheet | ✅ Yes |
| **n8n Cloud account** | Free trial at n8n.io | ❌ Need to create |

---

## PHASE 1 — Prepare Your Google Sheet (10 minutes)

### Step 1.1 — Open Your Google Sheet

1. Go to: https://docs.google.com/spreadsheets/d/1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs/edit
2. You should see tabs at the bottom: **Student Registry**, **Daily Responses**, **Bot Session** (or similar), **Dashboard**

### Step 1.2 — Verify Student Registry Tab

Click the **Student Registry** tab. Make sure the first row (Row 1) has these exact column headers (spelling matters):

```
student_name | telegram_chat_id | batch_group | start_date | optional_subject | Expected Next | Session Date
```

**If `Expected Next` and `Session Date` are missing:**
1. Click on the first empty column header in Row 1 (after `optional_subject`)
2. Type: `Expected Next`
3. Click the next empty column
4. Type: `Session Date`
5. Press Ctrl+S (or Cmd+S on Mac) to save

### Step 1.3 — Verify Daily Responses Tab

Click the **Daily Responses** tab. Row 1 must have these headers (in any order):

```
Date | Day Number | Student Name | Telegram Chat ID | Slots Target | Hours Target | Completion Status | Actual Hours | Productivity | Morning Timestamp | Night Timestamp
```

**If any column is missing**, add it to the first empty column in Row 1.

### Step 1.4 — Verify student data exists

In **Student Registry**, check that your students' rows have:
- `student_name` — student's full name
- `telegram_chat_id` — their Telegram Chat ID number (NOT their username)
- `start_date` — in format `DD/MM/YYYY` (e.g., `01/04/2026`)

> **How to get a student's Telegram Chat ID:**
> Ask them to message the bot. Go to:
> `https://api.telegram.org/bot8711874086:AAG3vXsuGQuHc8VXbL-hiJI7YVGpg71j_AY/getUpdates`
> Find `"chat": {"id": 123456789}` — that number is their Chat ID.

---

## PHASE 2 — Create n8n Cloud Account (5 minutes)

### Step 2.1 — Sign Up for n8n Cloud

1. Go to **https://n8n.io**
2. Click **"Get started for free"**
3. Sign up with your email
4. Choose the **Starter** plan (free trial, no credit card needed initially)
5. When asked for an instance name, type something like `laexcellence` or `irmentor`
6. Your instance URL will be something like: `https://laexcellence.app.n8n.cloud`
   → **Write this URL down in your notepad**

### Step 2.2 — Get Your n8n API Key

1. Inside n8n, click your **profile icon** (bottom-left corner)
2. Click **"Settings"**
3. Click **"API"** in the left menu
4. Click **"Create an API key"**
5. Give it a name like `setup-key`
6. Copy the key that appears — it looks like a long string of letters/numbers
   → **Write this key down in your notepad** (you can only see it once!)

---

## PHASE 3 — Add Telegram Credential (3 minutes)

### Step 3.1 — Create Telegram Credential

1. In n8n, click **"Credentials"** in the left sidebar
2. Click **"Add credential"** (top right)
3. In the search box, type `Telegram`
4. Click **"Telegram API"**
5. In the **"Access Token"** field, paste your bot token:
   ```
   8711874086:AAG3vXsuGQuHc8VXbL-hiJI7YVGpg71j_AY
   ```
6. Click **"Save"**
7. You'll see the credential listed. Click on it.
8. Look at the URL in your browser — it will say something like `/credentials/abc123xyz`
   → **Write down the credential ID** (the `abc123xyz` part)

---

## PHASE 4 — Add Google Sheets Credential (5 minutes)

### Step 4.1 — Create Google Sheets Credential

1. In n8n, click **"Credentials"** in the left sidebar
2. Click **"Add credential"**
3. In the search box, type `Google Sheets`
4. Click **"Google Sheets OAuth2 API"**
5. Click **"Sign in with Google"** (a popup will appear)
6. Select your Google account (the one that owns the spreadsheet)
7. Click **"Allow"** to give n8n access to Google Sheets
8. The popup closes — you'll see "Connected" in green ✅
9. Click **"Save"**
10. Look at the credential URL again → **Write down the Google Sheets credential ID**

---

## PHASE 5 — Import All 5 Workflows (15 minutes)

You will import the 5 workflow files one by one. **Import in the order shown below.**

The 5 files are in the folder: `n8n_workflows/`
```
01_morning_checkin.json
02_afternoon_nudge.json
03_night_checkin.json
04_capture_replies.json
05_weekly_summary.json
```

### Step 5.1 — How to Import a Workflow

For **each** of the 5 files, do this:

1. In n8n, click **"Workflows"** in the left sidebar
2. Click **"Add Workflow"** (top right)
3. In the new empty workflow, click the **"..."** menu (three dots, top right)
4. Click **"Import from file"**
5. Select the workflow JSON file from your computer
6. The workflow will load — you'll see all the nodes connected

### Step 5.2 — Connect Credentials After Each Import

After importing **each** workflow, you must connect credentials to the nodes:

**For any node that shows a red warning (credential missing):**
1. Click on that node
2. Look for the **"Credential"** dropdown
3. Select your Google Sheets account OR your Telegram API credential
4. Click outside the node to close it

**Nodes that need Google Sheets credential:**
- "Read Student Registry"
- "Set Session — waiting_slots" (or any "Set Session" node)
- "Lookup Today's Morning Targets"
- "Read Student's Responses"

**Nodes that need Telegram credential:**
- "Send Afternoon Nudge"
- "Send Weekly Summary"
- "Send Weekly Summary"

> **Note:** Nodes that use HTTP Request directly (like "Send Morning Q1", "Send Night Q1") do NOT need a credential — they use the bot token embedded in the URL.

### Step 5.3 — Save Each Workflow

After connecting credentials, click **"Save"** (top right of the workflow editor).

---

## PHASE 6 — Activate All Workflows (2 minutes)

**Activate in this exact order:**

1. Open **04 — Capture Replies** workflow → Toggle the switch at top to **ON** (green)
2. Open **01 — Morning Check-in** → Toggle **ON**
3. Open **02 — Afternoon Nudge** → Toggle **ON**
4. Open **03 — Night Check-in** → Toggle **ON**
5. Open **05 — Weekly Summary** → Toggle **ON**

> Workflow 04 must be active first because it listens for all student replies. If it's off, replies are lost.

---

## PHASE 7 — Test That It Works (5 minutes)

### Test 1 — Morning Check-in

1. Open **Workflow 01 — Morning Check-in**
2. Click **"Test Workflow"** (top right)
3. Wait 10-15 seconds
4. Check your Telegram — every student with a Chat ID should receive:
   > "🌞 Good Morning! How many study slots are you targeting today?" + keyboard buttons

### Test 2 — Reply Capture

1. On your phone, open Telegram and find **@Irmentor_bot**
2. Tap one of the keyboard buttons (e.g., "4 Slots")
3. The bot should reply: "Great! How many hours are you targeting?"
4. Type a number like `6` and send
5. The bot should confirm and thank you
6. Check Google Sheet → **Daily Responses** tab → you should see a new row with today's data

### Test 3 — Night Check-in

1. Open **Workflow 03 — Night Check-in**
2. Click **"Test Workflow"**
3. Students should receive the evening check-in with ✅/⚠️/❌ buttons

---

## Troubleshooting

### "No messages arriving in Google Sheet"
- Check that **Workflow 04 (Capture Replies)** is Active (green toggle)
- In n8n Cloud, Telegram webhook is set automatically — no ngrok needed ✅

### "Bot not responding to keyboard taps"
- The keyboard buttons send text messages — make sure Workflow 04 is ON
- Check Workflow 04 execution history for errors

### "Error on Google Sheets node"
- Your Google Sheets credential may have expired
- Go to Credentials → delete and re-add Google Sheets credential
- Reconnect it to all affected nodes

### "Students getting messages at wrong time"
- All times are pre-set in IST (India Standard Time)
- n8n Cloud automatically handles timezone — no changes needed

### "I added a new student — will they get messages?"
- Yes! Just add their row to **Student Registry** with correct `telegram_chat_id`
- The bot reads the sheet fresh every day

---

## Daily Operations (Once Set Up)

**Nothing to do daily** — the bot runs automatically.

**Weekly check (5 minutes):**
1. Look at **Daily Responses** tab for any students with missing data
2. Check if any student's `telegram_chat_id` is empty (they haven't started yet)

**Adding a new student:**
1. Go to **Student Registry** → add a new row
2. Fill: student_name, telegram_chat_id, batch_group, start_date, optional_subject
3. Done — they'll get the next scheduled message automatically

---

## Quick Reference Card

| Thing | Value |
|-------|-------|
| Bot Name | @Irmentor_bot |
| Bot Token | `8711874086:AAG3vXsuGQuHc8VXbL-hiJI7YVGpg71j_AY` |
| Google Sheet ID | `1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs` |
| Morning time | 7:00 AM IST |
| Afternoon time | 2:00 PM IST |
| Night time | 9:30 PM IST |
| Weekly report | Sunday 10:00 AM IST |
| n8n Cloud URL | Your instance URL (noted in Step 2.1) |

---

## Getting Help

If something isn't working:
1. In n8n, click **"Executions"** (left sidebar) to see what happened
2. Click on a failed execution (red) to see the error message
3. Share the error message with your technical support person

---

*Guide prepared for LA Excellence Mentorship Program — n8n Cloud deployment*
