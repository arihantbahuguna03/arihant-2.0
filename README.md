# Arihant 2.0

**Your AI Chief of Staff for Slack.**

An AI layer that sits on top of your Slack inbox — learns how you communicate, acts on your behalf when the answer is known, escalates when it isn't, and delivers a twice-daily prioritised brief so you spend your attention on what actually needs you.

> Built using Claude 3.5 Sonnet API + Slack SDK. Raw API calls — no agent framework.
> Designed for PMs, founders, and ops leads managing multiple parallel threads, stakeholder follow-ups, and recurring questions simultaneously.

---

## The Problem

High-context knowledge workers deal with:
- Multiple threads open across channels at once
- Repeated questions they've already answered 10 times
- Follow-ups they promised but forgot to send
- No system to separate what's actually urgent from what just feels urgent

The result: context-switching kills deep work, things fall through the cracks.

---

## What Arihant 2.0 Does

### 1. Intelligent Inbox
Classifies every message into what it actually needs from you:
- **Action required** — you need to do something
- **Reply required** — someone asked you something
- **Follow-up owed** — you said you'd do something
- **FYI** — informational, no action needed

### 2. Reply Memory Engine
Every reply you send is stored and semantically indexed. The bot learns:

| Pattern | Past uses | Confidence | Action |
|---|---|---|---|
| "Where's the access form?" | 9× | HIGH | Auto-reply |
| "What's the integration ETA?" | 2× | MEDIUM | Suggest + 1-tap approve |
| "Should we do X or Y?" | 0× | NEW | Hold + draft for you |

Confidence degrades when you correct the bot. It learns from every override.

### 3. Three-Mode Reply Dispatch

**HIGH confidence** → auto-replies on your behalf
> *"Hey! Here's the access request form: [link]. Let me know if you need anything else."*

**MEDIUM confidence** → sends you a 1-tap approval
> *Notification: "Priya asked about meeting slots. You've answered this 4 times. Suggested reply: [draft]. Approve / Edit / Skip"*

**LOW / NEW** → posts hold message in thread, sends you a recommended draft
> *Thread: "Hey Priya, Arihant will get back to you shortly!"*
> *You receive: "Priya asked about X. Here's what I'd recommend you say: [draft]."*

### 4. Priority Engine
Scores every open item across 5 dimensions:

| Dimension | Signal |
|---|---|
| Sender level | Founder / VP / direct report / peer / external |
| Urgency language | "blocker", "P0", "urgent", "EOD", "deadline" |
| Age | How long it's been waiting unreplied |
| Channel context | #incidents > #leadership > #product > #random |
| Project phase | Launch week items rank higher |

Output: a ranked list — not alphabetical, not chronological — **prioritised by what needs you first**.

### 5. Twice-Daily Digest
Delivered at 12:00 and 19:00 (configurable). Claude writes a 250-word actionable brief:

```
ARIHANT 2.0 — MID-DAY BRIEF | Nov 3, 12:00

3 items need you before EOD, 1 is a P0.

🔴 NEEDS YOU NOW
  1. [P0] Vikram in #incidents — payout job failed, needs sign-off (25m ago)
     Reason: P0 keyword, incident channel, direct report
  2. [P1] Rahul in #leadership — Q3 summary before 4pm call (2h ago)
     Reason: VP sender, time-sensitive

🟡 REPLY WHEN YOU CAN
  3. [P1] Neha in #product — roadmap call slots (45m ago)
  4. [P2] Arjun in #ops — integration ETA (4h ago)

YOUR 3 ACTIONS RIGHT NOW:
  → Sign off on payout retry (Vikram, #incidents)
  → Send Q3 summary to Rahul (before 3:30pm)
  → Reply to Neha with calendar link

✅ BOT HANDLED TODAY: 3 auto-replies (access form × 2, standup format × 1)
⏰ YOU OWE: Ananya is following up on campaign metrics from yesterday
```

### 6. Skill Triggers
For recurring questions with automatable answers:

> "What's the current success rate?" →  runs `query_success_rate` skill → auto-replies with live data

Configure your own skill triggers in `config.py`. Skills are Python functions that connect to your data sources.

---

## Architecture

```
Slack API (or demo_data.py in demo mode)
    └── slack_reader.py       — fetch + normalise messages
            └── classifier.py — Claude classifies each message type + extracts core question
                    ├── skill_triggers.py  — skill pattern match → run skill → auto-reply
                    └── reply_engine.py    — memory match → HIGH/MEDIUM/LOW dispatch
                            ├── memory.py          — SQLite reply memory + confidence scoring
                            ├── priority_engine.py — score + rank open items
                            └── digest.py          — Claude writes twice-daily brief
```

---

## Files

| File | Description |
|---|---|
| `main.py` | Entry point — runs the full pipeline |
| `slack_reader.py` | Slack API integration + demo mode |
| `classifier.py` | Message classification via Claude |
| `memory.py` | Reply memory store + confidence scoring |
| `reply_engine.py` | HIGH/MEDIUM/LOW reply dispatch |
| `priority_engine.py` | 5-dimension priority scoring |
| `skill_triggers.py` | Skill pattern matching + execution |
| `digest.py` | Twice-daily brief generation via Claude |
| `config.py` | All thresholds, weights, schedule settings |
| `demo_data.py` | Synthetic Slack messages (no real data) |

---

## Run Locally (Demo Mode)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
python main.py
```

Digest only:
```bash
python main.py --digest
```

---

## Production Setup

```bash
# Set Slack bot token
export SLACK_BOT_TOKEN=xoxb-your-token-here
export ANTHROPIC_API_KEY=your_key_here

# Run live
python main.py --live

# Schedule with cron (twice daily)
0 12 * * 1-5 cd /path/to/arihant-2.0 && python main.py --live
0 19 * * 1-5 cd /path/to/arihant-2.0 && python main.py --live
```

---

## Design Decisions

| Decision | Reasoning |
|---|---|
| Confidence based on use-count + corrections | Pure frequency is naive. A reply you've given 10 times but corrected 5 times should be MEDIUM, not HIGH |
| Skill triggers run before memory lookup | Skills return live data, not canned replies. They should always win when a pattern matches |
| Hold message posted before you approve | Prevents the sender from waiting with no acknowledgment while you decide what to reply |
| SQLite for memory | Simple, portable, no infra. In production, swap for a vector DB for semantic search at scale |
| Claude for digest, not template | Template digests get ignored after day 3. A brief written fresh each time reads like a human wrote it |
| Digest at 12:00 and 19:00 | Mid-day: course-correct the afternoon. End-of-day: clear your head and plan tomorrow |
