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
