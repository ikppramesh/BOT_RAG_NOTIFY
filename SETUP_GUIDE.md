# LA Excellence Mentorship Bot — Complete Setup Guide

**Telegram Bot + Google Sheets + n8n Automation**
No coding required. Follow each step in order.

---

## Table of Contents

1. [Overview — What You Will Build](#1-overview)
2. [Create the Telegram Bot](#2-create-the-telegram-bot)
3. [Create the Google Sheet](#3-create-the-google-sheet)
4. [Set Up n8n](#4-set-up-n8n)
5. [Connect Credentials in n8n](#5-connect-credentials-in-n8n)
6. [Import & Configure the 4 Workflows](#6-import--configure-the-4-workflows)
7. [Onboard Students](#7-onboard-students)
8. [Test the System](#8-test-the-system)
9. [Go Live with All Students](#9-go-live-with-all-students)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Overview

You will build a system with 3 parts that talk to each other automatically:

```
TELEGRAM BOT          n8n (Automation)        GOOGLE SHEETS
─────────────         ────────────────        ─────────────
Sends messages   ←→   Schedules & routes  →   Stores all data
to students           all messages            you can review
```

**The 4 automated workflows:**

| # | Workflow | When It Runs |
|---|---|---|
| 01 | Morning Check-in | Every day at 7:00 AM IST |
| 02 | Evening Check-in | Every day at 9:00 PM IST |
| 03 | Capture Replies | Always-on (24/7 listener) |
| 04 | Weekly Summary | Every Sunday at 10:00 AM IST |

---

## 2. Create the Telegram Bot

**Time needed: ~10 minutes**

### Step 2.1 — Create the bot via BotFather

1. Open **Telegram** on your phone or desktop.
2. In the search bar, search for **`@BotFather`** — tap the result with the blue verified checkmark.
3. Tap **START** (or type `/start`).
4. Type `/newbot` and press send.
5. BotFather asks for a **display name** — type:
   ```
   LA Excellence Mentorship Bot
   ```
6. BotFather asks for a **username** (must end in `bot`) — type:
   ```
   Irmentor_bot
   ```

7. BotFather sends back your **API Token**. It looks like:
   ```
   8711874086:AAG3vXsuGQuHc8VXbL-hiJI7YVGpg71j_AY
   ```

> **Save this token immediately.** Copy it to a notes file on your computer AND your phone.
> Never share it publicly — anyone with this token can control your bot.

---

### Step 2.2 — Customize the bot (recommended)

Still in BotFather chat, send these commands one by one:

```
/setdescription
```
When prompted, paste:
```
LA Excellence Daily Accountability Bot — Track your UPSC preparation with daily morning and evening check-ins.
```

```
/setabouttext
```
When prompted, paste:
```
Automated daily check-in for LA Excellence IAS Academy mentorship students. Built with love for UPSC aspirants.
```

```
/setuserpic
```
When prompted, send the LA Excellence logo image.

---

### Step 2.3 — Note your Bot Username

Write down:
- **Bot Token:** `7xxxxxxxxx:AAH...` ← from Step 2.1
- **Bot Username:** `@Irmentor_bot`

---

## 3. Create the Google Sheet

**Time needed: ~20 minutes**

### Step 3.1 — Create the spreadsheet

1. Go to [sheets.google.com](https://sheets.google.com) and sign in with your Google account.
2. Click the **`+`** button (Blank spreadsheet).
3. Click the title at the top (it says "Untitled spreadsheet") and rename it to:
   ```
   LA Excellence — Daily Accountability Tracker 2026
   ```
4. At the bottom of the screen, you will see **"Sheet1"** tab. Create 3 tabs total:
   - Click the **`+`** button at bottom-left to add sheets.
   - Name them exactly (spelling matters for n8n):
     - `Daily Responses`
     - `Student Registry`
     - `Dashboard`

---

### Step 3.2 — Set up "Student Registry" tab

Click the **Student Registry** tab. In **Row 1**, type these headers exactly as shown (one per cell, A1 through F1):

| A1 | B1 | C1 | D1 | E1 | F1 |
|---|---|---|---|---|---|
| `student_name` | `phone_number` | `telegram_chat_id` | `batch_group` | `start_date` | `optional_subject` |

> **Why lowercase with underscores?** n8n references these column names in the workflow. Using lowercase with underscores avoids errors.

**Example data rows (add your students here):**

| student_name | phone_number | telegram_chat_id | batch_group | start_date | optional_subject |
|---|---|---|---|---|---|
| Swathi Reddy | 9876543210 | 1234567890 | Batch-2027-A | 01/10/2025 | Anthropology |
| Arjun Kumar | 9876543211 | 1234567891 | Batch-2027-A | 01/10/2025 | Geography |

> **How to get a student's Telegram Chat ID:** See [Step 7.2](#72--get-each-students-telegram-chat-id) below.

---

### Step 3.3 — Set up "Daily Responses" tab

Click the **Daily Responses** tab. In **Row 1**, type these exact headers (A1 through N1):

| Cell | Header (type exactly) |
|---|---|
| A1 | `Date` |
| B1 | `Student Name` |
| C1 | `Telegram Chat ID` |
| D1 | `Morning Target` |
| E1 | `Planned Subjects` |
| F1 | `Planned Hours` |
| G1 | `Evening Status` |
| H1 | `Hours Completed` |
| I1 | `Hours Label` |
| J1 | `Subjects Covered` |
| K1 | `Test Written Today?` |
| L1 | `Productivity (1-5)` |
| M1 | `Blockers/Notes` |
| N1 | `Timestamp` |

Leave all other rows empty — n8n will fill them automatically.

---

### Step 3.4 — Set up "Dashboard" tab

Click the **Dashboard** tab. Add these formulas to track progress at a glance:

| Cell | Type This Formula | What It Shows |
|---|---|---|
| B2 | `=COUNTIF('Daily Responses'!A:A,TEXT(TODAY(),"dd/mm/yyyy"))` | Students who reported today |
| B3 | `=COUNTA('Student Registry'!A:A)-1` | Total enrolled students |
| B4 | `=B3-B2` | Students who haven't reported today |
| B6 | `=COUNTIF('Daily Responses'!G:G,"Fully Done")/COUNTA('Daily Responses'!G:G)` | Overall target completion rate |
| B7 | `=AVERAGE('Daily Responses'!H:H)` | Average hours per day (all students) |
| B8 | `=AVERAGE('Daily Responses'!L:L)` | Average productivity score |

Add labels in column A next to each formula (A2 = "Reported Today", A3 = "Total Students", etc.).

---

### Step 3.5 — Get the Spreadsheet ID

You will need this ID to connect n8n to your sheet.

1. Look at the URL in your browser while the sheet is open. It looks like:
   ```
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit
   ```
2. The long string between `/d/` and `/edit` is your **Spreadsheet ID**:
   ```
   1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs
   ```
3. This ID is already filled into all 4 workflow JSON files — no manual replacement needed.

---

## 4. Set Up n8n

**Time needed: ~10 minutes**

### Step 4.1 — Create your n8n account

1. Go to [n8n.io](https://n8n.io) in your browser.
2. Click **"Get Started Free"**.
3. Sign up with your email address.
4. Verify your email.
5. You are now in the **n8n dashboard** — a blank canvas where you build workflows.

**Which plan do you need?**

| Students | Executions/Month | Plan Needed |
|---|---|---|
| Up to ~40 students (testing) | ~2,400/month | Free tier |
| 80+ students (full launch) | ~5,000/month | Starter — $20/month |

> Start on the free tier for testing with 5 students. Upgrade before the full launch.

---

## 5. Connect Credentials in n8n

**Time needed: ~15 minutes**

You need to connect your Telegram bot and Google account to n8n. Do this once — all 4 workflows will use these same credentials.

### Step 5.1 — Add your Telegram Bot credential

1. In n8n, click your account name (top-right) → **Settings**.
2. Click **Credentials** in the left sidebar.
3. Click **"+ Add Credential"**.
4. Search for **"Telegram"** and select it.
5. In the **"API Token"** field, paste your bot token from Step 2.1.
6. Click **"Save"**.
7. Write down the **Credential Name** (e.g., "Telegram API") — you will need it when configuring workflows.

---

### Step 5.2 — Add your Google Sheets credential

1. In n8n Credentials, click **"+ Add Credential"** again.
2. Search for **"Google Sheets"** and select **"Google Sheets OAuth2 API"**.
3. Click **"Sign in with Google"**.
4. A browser window opens — sign in with the Google account that owns your spreadsheet.
5. Click **"Allow"** to give n8n access to your Google Sheets.
6. Back in n8n, click **"Save"**.
7. Write down the **Credential Name** (e.g., "Google Sheets account").

---

## 6. Import & Configure the 4 Workflows

**Time needed: ~30 minutes total**

The 4 workflow JSON files are located in the `n8n_workflows/` folder:
- `01_morning_checkin.json`
- `02_evening_checkin.json`
- `03_capture_replies.json`
- `04_weekly_summary.json`

### Step 6.1 — Spreadsheet ID is already set

The Spreadsheet ID `1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs` is already filled into all 4 JSON files. You can import them directly — no text editor edits needed.

---

### Step 6.2 — Import each workflow into n8n

For **each** of the 4 JSON files:

1. In n8n, click **"+ New Workflow"** (or the Workflows menu).
2. Click the **three-dot menu** (⋮) in the top-right of the canvas.
3. Select **"Import from file"**.
4. Select the JSON file (e.g., `01_morning_checkin.json`).
5. The workflow appears on the canvas.

---

### Step 6.3 — Connect credentials to each node

After importing, n8n shows credential warnings (yellow icons on nodes). Fix them:

1. Click any node that has the warning icon.
2. In the **Credentials** dropdown, select the credential you created in Step 5.
3. Repeat for every Google Sheets and Telegram node in every workflow.

> **Quick tip:** In each workflow, there are typically 2–3 nodes that need credentials. Click each yellow-outlined node, pick the correct credential, and save.

---

### Step 6.4 — Activate the workflows

| Workflow | How to Activate | When Active |
|---|---|---|
| 01 Morning Check-in | Toggle ON | Runs at 7 AM daily |
| 02 Evening Check-in | Toggle ON | Runs at 9 PM daily |
| **03 Capture Replies** | **Toggle ON** | **Must be always ON** |
| 04 Weekly Summary | Toggle ON | Runs Sunday 10 AM |

> **Most important:** Workflow 03 must be permanently ON. It is the listener that captures student replies. If it is off, no data will be saved to the sheet.

---

## 7. Onboard Students

**Time needed: ~5 minutes per student**

### Step 7.1 — Share the bot link

Send this message to your students (via WhatsApp, existing Telegram group, or email):

```
Dear students,

We are launching our new daily accountability system for your UPSC preparation! 📱

Please take 10 seconds to activate your daily check-ins:

1. Click this link: https://t.me/Irmentor_bot
   (replace with your actual bot username)
2. Tap the START button
3. That's it! You will receive your first check-in tomorrow morning at 7 AM.

This system will help you track your daily progress and help us give you better mentorship support. 🙏

— LA Excellence Team
```

---

### Step 7.2 — Get each student's Telegram Chat ID

When a student taps START, the bot receives their message. You can see their Chat ID in two ways:

**Method A — Check n8n execution logs:**
1. After a student taps START, go to n8n → Workflow 03 → **Executions** tab.
2. Click the latest execution.
3. Click the "Telegram Trigger" node result.
4. Look for `message.from.id` — that number is their Chat ID.

**Method B — Use a helper bot:**
1. Ask the student to also open `@userinfobot` on Telegram.
2. They type `/start` — it immediately replies with their Chat ID.
3. They send you that number.

Once you have the Chat ID, add it to the **Student Registry** sheet in the `telegram_chat_id` column.

---

## 8. Test the System

**Time needed: 1 day (you set your own schedule)**

### Step 8.1 — Test with 5 students first

1. Add 5 willing students to the Student Registry sheet.
2. Ensure all 4 workflows are **Active** (toggle ON).
3. **Manually trigger** the morning workflow for an immediate test:
   - Open Workflow 01 in n8n.
   - Click the **"Test workflow"** button (triangle/play icon).
   - Check if all 5 students receive the message on Telegram.

4. Ask each student to reply with a fake morning target. Check that:
   - Their reply appears in the **Daily Responses** sheet (columns A–F).
   - The bot sends a confirmation message back to them.

5. **Manually trigger** Workflow 02 (Evening) — verify students receive the 5-button questions.
6. Ask each student to tap all 5 buttons. Verify:
   - Each button tap updates the correct column in Daily Responses.
   - No duplicate rows are created (the same row for that date updates).

### Step 8.2 — Testing checklist

| Test | Expected Result | Pass? |
|---|---|---|
| Morning message sent | All test students receive it | ☐ |
| Student replies → sheet | Reply in column D (Morning Target) | ☐ |
| Confirmation bot message | Bot says "Morning target noted!" | ☐ |
| Evening 5 messages sent | All students receive button questions | ☐ |
| Each button tap recorded | Correct column updated in sheet | ☐ |
| No duplicate rows | Same date = same row, just updated | ☐ |
| Weekly summary (trigger manually) | Correct stats, no errors | ☐ |

---

## 9. Go Live with All Students

Once testing passes:

1. Add all 80+ students to the Student Registry sheet.
2. Give students 2–3 days to complete onboarding (tap START).
3. Confirm all workflows are Active.
4. Check Google Sheets every morning for the first week to verify data is flowing.
5. After the first week, you have enough data to start reviewing student patterns.

---

## 10. Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| Student didn't receive morning message | They haven't tapped START yet, or wrong Chat ID | Ask them to open the bot link and tap START. Re-verify their Chat ID. |
| Bot message delivered but reply not saving | Workflow 03 is OFF | Go to n8n → Workflow 03 → Toggle ON |
| Data appears in wrong column | Column header in sheet doesn't match exactly | Check spelling in Row 1 of Daily Responses against the header names in Step 3.3 |
| Button taps not recording | `appendOrUpdate` key columns mismatch | Ensure Daily Responses has `Date` and `Telegram Chat ID` as exact column headers (case-sensitive) |
| n8n workflow shows error | Spreadsheet ID wrong | Open the failing node, check `documentId` value matches your actual Spreadsheet ID |
| Student gets double confirmation | Running both test and live at same time | Only trigger manually during testing; switch to schedule for live |
| Weekly summary shows 0 hours | Student data in sheet uses different date format | Confirm dates in Daily Responses are in `DD/MM/YYYY` format |
| Credentials warning after import | Credentials not linked to nodes | Click each yellow-outlined node → select the correct credential → save |

---

## Reference: Callback Data Values

When students tap evening buttons, the following values are written to the sheet:

**Hours buttons:**
| Button Label | Value Saved |
|---|---|
| < 4 hours | `3` (Hours Completed) + `< 4 hours` (Hours Label) |
| 4–6 hours | `5` |
| 6–8 hours | `7` |
| 8+ hours | `9` |

**Subject buttons:**
| Button Label | Value Saved in "Subjects Covered" |
|---|---|
| GS Only | `GS Only` |
| Optional Only | `Optional Only` |
| Both GS & Optional | `Both GS & Optional` |
| Revision | `Revision` |

**Test buttons:**
| Button | Value in "Test Written Today?" |
|---|---|
| Yes | `Yes` |
| No | `No` |

**Productivity (1–5):** Saves the number directly.

**Target Status:**
| Button | Value in "Evening Status" |
|---|---|
| Fully Done | `Fully Done` |
| Partially Done | `Partially Done` |
| Not Done | `Not Done` |

---

## Quick Reference — Your Credentials

```
Bot Token:         8711874086:AAG3vXsuGQuHc8VXbL-hiJI7YVGpg71j_AY
Bot Username:      @Irmentor_bot
Bot Link:          https://t.me/Irmentor_bot

Spreadsheet ID:    1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs
Spreadsheet URL:   https://docs.google.com/spreadsheets/d/1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs/edit

n8n Account Email: ___________________________________  ← fill in when you create n8n account
Telegram Credential Name (in n8n): ________________    ← fill in after Step 5.1
Google Sheets Credential Name (in n8n): ____________   ← fill in after Step 5.2
```

---

*LA Excellence IAS Academy — Daily Accountability System*
*Questions? Ask your tech support contact.*
