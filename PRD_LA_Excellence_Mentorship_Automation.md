# LA EXCELLENCE IAS ACADEMY
## MENTORSHIP AUTOMATION GUIDE

**Telegram Bot + n8n + Google Sheets**  
**Complete Step-by-Step Implementation Guide**  
**Daily Student Accountability System**

---

> **For:** Kalyan Sir & LA Excellence Team  
> **Date:** March 2026  
>
> *No coding knowledge required. This guide is written for non-technical users.*  
> **Estimated setup time:** 3–5 hours (with a tech friend) or 6–8 hours (solo)

---

## TABLE OF CONTENTS

- [PART A: THE BIG PICTURE](#part-a-the-big-picture)
  - [What We Are Building](#what-we-are-building)
  - [Architecture Overview](#architecture-overview)
  - [What You Need Before Starting](#what-you-need-before-starting)
- [PART B: TELEGRAM BOT SETUP](#part-b-telegram-bot-setup)
  - [Step 1: Create Your Telegram Bot](#step-1-create-your-telegram-bot)
  - [Step 2: Set Up Student Onboarding](#step-2-set-up-student-onboarding)
- [PART C: GOOGLE SHEETS SETUP](#part-c-google-sheets-setup)
  - [Step 3: Create the Accountability Tracker Sheet](#step-3-create-the-accountability-tracker-sheet)
  - [Step 4: Sheet Structure & Columns](#step-4-sheet-structure--columns)
- [PART D: n8n SETUP & WORKFLOWS](#part-d-n8n-setup--workflows)
  - [Step 5: Create Your n8n Account](#step-5-create-your-n8n-account)
  - [Step 6: Build the Morning Check-in Workflow](#step-6-build-the-morning-check-in-workflow)
  - [Step 7: Build the Evening Check-in Workflow](#step-7-build-the-evening-check-in-workflow)
  - [Step 8: Build the Weekly Summary Workflow](#step-8-build-the-weekly-summary-workflow)
- [PART E: TESTING & LAUNCH](#part-e-testing--launch)
  - [Step 9: Test with 5 Students](#step-9-test-with-5-students)
  - [Step 10: Scale to 80+ Students](#step-10-scale-to-80-students)
- [PART F: APPENDICES](#part-f-appendices)
  - [Appendix A: Message Templates](#appendix-a-all-message-templates)
  - [Appendix B: Cost Summary](#appendix-b-cost-summary)
  - [Appendix C: Troubleshooting](#appendix-c-troubleshooting)
  - [Appendix D: Future Enhancements](#appendix-d-future-enhancements)

---

## PART A: THE BIG PICTURE

### What We Are Building

You are building an **automated daily accountability system** where every student in your mentorship program receives two messages each day:

- 🌞 **Morning Check-in (7:00 AM):** *"What are your study targets for today?"* — Students reply with their planned subjects and hours.
- 🌙 **Evening Check-in (9:00 PM):** *"How did your day go?"* — Students tap buttons to report hours completed, subjects covered, test status, and productivity score.

Every response is **automatically saved to a Google Sheet**. You (the mentor) can see at a glance which students are on track, who is falling behind, and who needs intervention.

---

### Architecture Overview

The system has three simple components that talk to each other:

| Component | What It Does | Cost |
|---|---|---|
| **Telegram Bot** | Sends messages to students, receives their replies | Free (forever) |
| **n8n (Automation)** | Schedules messages, processes replies, routes data | Free tier or ~$20/month |
| **Google Sheets** | Stores all student responses as a daily tracker | Free (Google account) |

**How the data flows:**

```
n8n triggers at 7:00 AM
        ↓
Sends message via Telegram Bot
        ↓
Student replies
        ↓
Telegram sends reply to n8n
        ↓
n8n writes data to Google Sheet
        ↓
You view the sheet anytime
```

---

### What You Need Before Starting

Before you begin setup, make sure you have the following ready:

| # | Item | Details | Time Needed |
|---|---|---|---|
| 1 | A Telegram account | Your personal Telegram app on phone + desktop | Already have it |
| 2 | A Google account | For Google Sheets (any Gmail will work) | Already have it |
| 3 | A computer/laptop | For n8n setup (one-time, then it runs on its own) | During setup only |
| 4 | Student Telegram IDs | Each student's Telegram username or chat ID | 5 min per student |
| 5 | 30 minutes of patience | The first setup takes focus, but it's a one-time effort | — |

> 💡 **Do you need a tech friend?**  
> Honestly, you can do Steps 1–4 completely on your own. For Steps 5–8 (the n8n workflows), having someone who has used a computer comfortably for basic tasks is enough. If you get stuck, any college student who is comfortable with technology can help. This is **NOT** software engineering — it is more like setting up a WhatsApp group with some extra automation.

---

## PART B: TELEGRAM BOT SETUP

### Step 1: Create Your Telegram Bot
**⏱ Time required: ~10 minutes**

A Telegram "bot" is like a virtual assistant that lives inside Telegram. It can send and receive messages automatically. Creating one is **free** and takes just a few minutes.

#### Instructions:

1. Open Telegram on your phone or desktop.
2. In the search bar, type **`@BotFather`** and tap the verified account (it has a blue tick ✅).
3. Tap **START** or type `/start` to begin.
4. Type `/newbot` and press send.
5. BotFather asks: *"What name do you want for your bot?"* — Type: `LA Excellence Mentorship Bot`
6. BotFather asks: *"Choose a username for your bot."* — Type: `LAExcellence_Mentor_bot` *(must end with "bot")*
7. BotFather will reply with a message containing your **API Token**. It looks like:

```
7123456789:AAHxyz_abc123def456ghi789
```

> ⚠️ **CRITICAL: Save this API Token safely!**  
> Copy it to a note on your phone **AND** a document on your computer. You will need this token in Step 5 when connecting to n8n.  
> **Never share this token publicly** — anyone with it can control your bot.

#### Customize Your Bot (Optional but Recommended):

While still in the BotFather chat, you can:

- Type `/setdescription` → Set it to: *"LA Excellence Daily Accountability Bot — Track your UPSC preparation daily"*
- Type `/setabouttext` → Set it to: *"Automated daily check-in for LA Excellence IAS Academy mentorship students"*
- Type `/setuserpic` → Upload the LA Excellence logo as the bot's profile picture

---

### Step 2: Set Up Student Onboarding
**⏱ Time required: ~15 minutes**

Each student needs to "start" a conversation with your bot before it can send them messages. Here is how to onboard students:

#### For each student:

1. Share the bot link with the student: `https://t.me/LAExcellence_Mentor_bot` *(replace with your actual bot username)*
2. Ask them to open the link and tap **"START"** in Telegram.
3. Once they tap START, the bot can now send them messages.
4. Note down each student's **Telegram Chat ID** (you'll need this for n8n). To get it: the student types `/start` to your bot, and n8n will capture their chat ID automatically *(we'll set this up in Step 6)*.

> 📣 **Batch onboarding tip:**  
> Send the bot link in your existing WhatsApp/Telegram group with a message like:  
> *"Dear students, we are launching our new AI-powered daily accountability system. Please click this link and tap START to activate your daily mentorship check-ins. This takes 10 seconds."*

#### Student Registration Sheet:

Create a simple Google Sheet called **"Student Registry"** with these columns:

| Column | Example | How to Get It |
|---|---|---|
| Student Name | Swathi | You already have this |
| Phone Number | 9876543210 | From your existing records |
| Telegram Chat ID | 1234567890 | Auto-captured when they `/start` the bot |
| Batch/Group | Batch 2027-A | Your classification |
| Start Date | 2025-10-14 | When they joined mentorship |
| Optional Subject | Anthropology | From intake form |

---

## PART C: GOOGLE SHEETS SETUP

### Step 3: Create the Accountability Tracker Sheet
**⏱ Time required: ~15 minutes**

This is the **master sheet** where every student's daily data will be stored. One row = one student's one day.

#### Instructions:

1. Go to [sheets.google.com](https://sheets.google.com) and sign in.
2. Click **"+"** to create a new spreadsheet.
3. Name it: **`LA Excellence — Daily Accountability Tracker 2026`**
4. Create the following tabs (sheets) at the bottom:
   - `Daily Responses`
   - `Student Registry`
   - `Dashboard`

---

### Step 4: Sheet Structure & Columns

#### Tab 1: Daily Responses

This is where every check-in response lands. Set up these column headers in **Row 1**:

| Column | Header Name | Data Type | Source |
|---|---|---|---|
| A | Date | Date (DD/MM/YYYY) | Auto from n8n |
| B | Student Name | Text | From registry |
| C | Telegram Chat ID | Number | Auto from Telegram |
| D | Morning Target | Text | Student's morning reply |
| E | Planned Subjects | Text | Student's selection (GS/Optional/Both) |
| F | Planned Hours | Number | Student's morning reply |
| G | Evening Status | Text | Completed / Partially / Not Done |
| H | Hours Completed | Number | Student's evening reply |
| I | Subjects Covered | Text | Student's evening selection |
| J | Test Written Today? | Yes/No | Button tap |
| K | Test Score (if any) | Number | Student's input |
| L | Productivity (1-5) | Number | Student's self-rating |
| M | Blockers/Notes | Text | Optional free text |
| N | Timestamp | DateTime | Auto from n8n |

#### Tab 2: Dashboard (Simple Formulas)

You can add simple formulas to track patterns. Here are some useful ones:

| Metric | Formula (put in Dashboard tab) | What It Shows |
|---|---|---|
| Avg hours/student | `=AVERAGEIF(B:B,"Swathi",H:H)` | Swathi's avg daily hours |
| Completion rate | `=COUNTIF(G:G,"Completed")/COUNTA(G:G)` | % of days fully completed |
| Students who reported today | `=COUNTIF(A:A,TODAY())` | How many responded today |
| Missing students | `=Total students - COUNTIF(A:A,TODAY())` | Who hasn't responded |

---

## PART D: n8n SETUP & WORKFLOWS

> 🔧 **What is n8n?**  
> n8n (pronounced *"n-eight-n"*) is a **visual automation tool**. Think of it like a flowchart that actually runs. You drag and drop blocks like "Send Telegram Message" and "Write to Google Sheet" and connect them with lines. When the flowchart runs, it actually does those things. **No coding needed.**

---

### Step 5: Create Your n8n Account
**⏱ Time required: ~10 minutes**

1. Go to [n8n.io](https://n8n.io) in your web browser.
2. Click **"Get Started Free"** (the cloud version).
3. Sign up with your email. The free tier gives you **2,500 executions/month**. For 80 students with 2 messages/day, that's about 4,800/month — so you'll need the **Starter plan at $20/month**. But start with free for testing.
4. Once logged in, you'll see the **n8n dashboard**. This is where you'll build your workflows.

#### Connect Your Credentials:

Before building workflows, you need to tell n8n about your Telegram bot and Google Sheet:

**Telegram Connection:**
1. In n8n, go to **Settings → Credentials → Add Credential**
2. Search for **"Telegram"**
3. Paste your **Bot API Token** from Step 1
4. Click **"Save"**. Done! ✅

**Google Sheets Connection:**
1. In n8n, go to **Settings → Credentials → Add Credential**
2. Search for **"Google Sheets"**
3. Click **"Sign in with Google"** and authorize your account
4. Select the Google account that has your tracker sheet
5. Click **"Save"**. Done! ✅

---

### Step 6: Build the Morning Check-in Workflow
**⏱ Time required: ~30 minutes**

This is the **main workflow**. It sends a morning message to all students at 7:00 AM and saves their replies.

#### Create the Workflow:

1. Click **"New Workflow"** in n8n.
2. Name it: **`Morning Check-in — Daily`**
3. You'll see a blank canvas. Now we add nodes (blocks):

---

#### Node 1: Schedule Trigger

- Click the **"+"** button on the canvas.
- Search for **"Schedule Trigger"** and add it.
- Set it to: **Trigger at 7:00 AM, Every Day, Timezone: Asia/Kolkata**
- This tells n8n: *"Run this workflow every morning at 7 AM."*

#### Node 2: Google Sheets — Read Student List

- Add a new node: **"Google Sheets"**
- Operation: **"Read Rows"**
- Select your spreadsheet: `LA Excellence — Daily Accountability Tracker 2026`
- Select sheet tab: `Student Registry`
- This reads all student names and their Telegram Chat IDs.

#### Node 3: Loop Over Students

- Add node: **"Split In Batches"** *(this processes one student at a time)*
- Batch size: `1`

#### Node 4: Telegram — Send Morning Message

- Add node: **"Telegram"**
- Operation: **"Send Message"**
- Chat ID: Use the expression `{{ $json.telegram_chat_id }}` *(this pulls each student's ID from the sheet)*
- **Message Text** *(copy this exactly)*:

```
🌞 Good Morning, {{ $json.student_name }}!

Time for your daily accountability check-in.

What are your study targets for today?

Please reply with:
1. Subjects you plan to cover
2. Hours you plan to study
3. Any specific goals (test, answer writing, revision)

Example: "Polity (Laxmikanth Ch 5-6), Optional (2h), MCQ practice (1h). Total: 7h"
```

#### Node 5: Wait for Reply

This is slightly advanced. You have two approaches:

> **Approach A (Simpler — Recommended): Separate reply-capture workflow**  
> Instead of waiting in the same workflow, create a **second workflow** that listens for incoming messages:
> 1. Create a new workflow: **`Capture Student Replies`**
> 2. Add node: **"Telegram Trigger"** *(this activates whenever anyone sends a message to your bot)*
> 3. Add node: **"Google Sheets — Append Row"** to write the reply to the Daily Responses tab
> 4. Map fields: Date = today's date, Student Name = from registry lookup, Morning Target = message text

> 💡 **Key Insight:**  
> You actually need **TWO workflows**: (1) the scheduled sender that pushes messages out, and (2) the always-on listener that captures replies. This is the **standard pattern** for Telegram bots in n8n.

---

### Step 7: Build the Evening Check-in Workflow
**⏱ Time required: ~30 minutes**

This workflow sends the evening accountability message at **9:00 PM** with quick-tap buttons.

#### Create the Workflow:

1. Create a new workflow: **`Evening Check-in — Daily`**
2. Add the same **Schedule Trigger**, but set to **9:00 PM**.
3. Add Google Sheets read (Student Registry).
4. Add **Split In Batches**.
5. Add **Telegram Send Message** with inline keyboard buttons:

#### Evening Message with Buttons:

In the Telegram node, set the **Reply Markup** to **"Inline Keyboard"** and configure the message:

```
🌙 Good Evening, {{ $json.student_name }}!

Time for your daily progress report. Quick questions:

How many hours did you study today?
(Tap one)
```

**Inline keyboard buttons — Row 1 (Hours):**

| Button 1 | Button 2 | Button 3 | Button 4 |
|---|---|---|---|
| `< 4 hours` | `4-6 hours` | `6-8 hours` | `8+ hours` |

The bot then asks follow-up questions using the same pattern:

| Question | Button Options |
|---|---|
| What did you focus on? | `GS Only` \| `Optional Only` \| `Both GS & Optional` \| `Revision` |
| Did you write a test today? | `Yes — Score?` \| `No Test Today` |
| Rate your productivity (1-5) | `1 ⭐` \| `2 ⭐` \| `3 ⭐` \| `4 ⭐` \| `5 ⭐` |
| Did you complete your morning target? | `Fully Done` \| `Partially` \| `Not Done` |

#### How Button Responses Work in n8n:

When a student taps a button, Telegram sends a **"callback query"** to n8n. Your reply-capture workflow (from Step 6) should also have a **"Telegram Trigger"** set to listen for callback queries. Each button has a **callback data value** (like `hours_4_6` or `productivity_3`) that you map to the correct Google Sheet column.

> 💡 **The entire evening check-in takes a student less than 30 seconds.**  
> They just tap 4–5 buttons. No typing needed. This is the key to **high compliance** — make reporting effortless.

---

### Step 8: Build the Weekly Summary Workflow
**⏱ Time required: ~20 minutes**

Every **Sunday at 10:00 AM**, send each student their weekly summary automatically.

#### Weekly Summary Message:

```
📊 Weekly Report for {{ $json.student_name }}

Week: Mar 17 - Mar 23, 2026

✅ Days Reported: 6/7
⏰ Total Hours: 45.5 hours
📝 Avg Productivity: 3.8/5
🎯 Targets Completed: 5/6 days
✍️ Tests Written: 2

Keep pushing, Swathi! Consistency is the key to cracking UPSC. 💪
```

This is generated by reading the past 7 days of data from Google Sheets for each student and calculating the totals using n8n's built-in formula nodes.

---

## PART E: TESTING & LAUNCH

### Step 9: Test with 5 Students
**⏱ Time required: 1 day**

1. Select **5 students** who are tech-comfortable and willing to give feedback.
2. Add their Telegram Chat IDs to the Student Registry sheet.
3. **Activate all three workflows** in n8n (Morning, Evening, Weekly).
4. Wait for the 7:00 AM trigger *(or manually trigger it for testing)*.
5. Check if all 5 students received the message.
6. Ask them to reply and verify data appears in Google Sheets.
7. Fix any issues (wrong Chat IDs, message formatting, etc.).

#### Testing Checklist:

| Test Item | Expected Result | Pass? |
|---|---|---|
| Morning message sent at 7 AM | All 5 students receive it | ☐ |
| Student replies with targets | Reply appears in Google Sheet column D | ☐ |
| Evening message sent at 9 PM | All 5 students receive it with buttons | ☐ |
| Button taps recorded | Correct values in Sheet columns G–L | ☐ |
| Weekly summary sent on Sunday | Correct stats for each student | ☐ |
| Missed student flagged | If someone doesn't respond, you can see it | ☐ |

---

### Step 10: Scale to 80+ Students
**⏱ Time required: 1 week**

1. After successful testing, **send the bot link to all 80 students**.
2. Give them **2–3 days to onboard** (tap START).
3. **Add all Chat IDs** to the Student Registry sheet.
4. **Activate the workflows.** The system now runs on autopilot.
5. **Check Google Sheets daily** for the first week to ensure data flows correctly.
6. After one week, you'll have enough data to identify patterns and start mentor interventions.

> 🏆 **Congratulations!**  
> You are now running **India's first Telegram-based automated UPSC mentorship accountability system**. Your students receive daily personalized check-ins, and you have real data to drive mentorship decisions.

---

## PART F: APPENDICES

### Appendix A: All Message Templates

#### Morning Message (Weekday):
```
🌞 Good Morning, {Name}!
Day {X} of your UPSC journey.

What are your study targets for today?
Reply with: Subjects | Hours | Goals

Remember: Consistency beats intensity. Even 4 focused hours beat 10 distracted hours. 💪
```

#### Morning Message (Sunday — Lighter):
```
🌟 Happy Sunday, {Name}!
It's your lighter day (6 hours target).

What's the plan?
Options: Light revision | Catch up | Rest day

Balance is key. Recharge today to power through the week. ☕
```

#### Missed Check-in Reminder (If no evening response by 10 PM):
```
🔔 Hi {Name}, you haven't submitted today's evening report yet.
Even if today wasn't productive, please report honestly.
Your mentor tracks consistency, not perfection. 🙏
```

---

### Appendix B: Cost Summary

| Item | Free Tier | Paid (Recommended) | Notes |
|---|---|---|---|
| Telegram Bot | Free forever | Free forever | No limits on messages |
| n8n Cloud | 2,500 runs/month | $20/month (Starter) | Need ~5,000 for 80 students |
| Google Sheets | Free | Free | Up to 10 million cells |
| Your Time | — | — | 30 min/week to review data |
| **TOTAL** | **Free (for testing)** | **$20/month** | That's ₹25/student/month! |

---

### Appendix C: Troubleshooting

| Problem | Likely Cause | Solution |
|---|---|---|
| Student didn't receive message | Wrong Chat ID or they didn't `/start` the bot | Verify Chat ID; ask them to reopen bot and tap START |
| n8n workflow not triggering | Workflow not activated | Toggle the "Active" switch to ON in n8n |
| Data not appearing in Sheet | Wrong sheet name or column mapping | Double-check spreadsheet name and tab name in n8n node |
| Buttons not working | Callback query not captured | Ensure Telegram Trigger node has "Callback Query" enabled |
| Messages arriving late | n8n cloud processing delay | Normal for free tier; paid tier is faster |

---

### Appendix D: Future Enhancements

Once the basic system is running, you can add these features over time:

| Phase | Timeline | Feature |
|---|---|---|
| **Phase 2** | Month 2 | **Mentor Dashboard** — A Google Data Studio report connected to your sheet, showing visual charts of student progress. |
| **Phase 3** | Month 3 | **Intelligent Alerts** — If a student misses 3 consecutive days, send an escalation message to you (the mentor) via Telegram. |
| **Phase 4** | Month 4 | **Study Planner Integration** — The morning message can reference the student's actual plan for that day (*"Today you're supposed to cover Polity Ch 5-6"*). |
| **Phase 5** | Month 5 | **Peer Accountability** — Weekly leaderboard of most consistent students shared in the group. |
| **Phase 6** | Month 6+ | **Migrate to LA Mentora App** — Full migration once the developer team is ready, with all this data as historical records. |

---

<div align="center">

## 🚀 YOUR ACCOUNTABILITY SYSTEM STARTS NOW!

**80 students. 2 messages a day. Zero manual effort.**  
**Real data. Real accountability. Real results.**

---

*LA Excellence IAS Academy*  
*First in India. Always.*

</div>
