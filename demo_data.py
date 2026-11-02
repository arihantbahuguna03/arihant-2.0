"""
Arihant 2.0 — Demo Slack Data
================================
Synthetic Slack messages for portfolio demonstration.
No real names, channels, workspace data, or message content from any company.
All persons, channels, and messages are fictional.
"""

from datetime import datetime, timedelta

NOW = datetime(2024, 11, 3, 18, 45, 0)

# ── Demo senders ──────────────────────────────────────────────────────────────
DEMO_SENDERS = {
    "U_RAHUL":   {"name": "Rahul",   "level": "vp",           "display": "Rahul V."},
    "U_PRIYA":   {"name": "Priya",   "level": "peer",         "display": "Priya S."},
    "U_VIKRAM":  {"name": "Vikram",  "level": "direct_report","display": "Vikram K."},
    "U_ANANYA":  {"name": "Ananya",  "level": "peer",         "display": "Ananya M."},
    "U_SIDDHARTH":{"name":"Siddharth","level":"peer",         "display": "Siddharth R."},
    "U_NEHA":    {"name": "Neha",    "level": "director",     "display": "Neha T."},
    "U_ARJUN":   {"name": "Arjun",   "level": "external",     "display": "Arjun (Partner)"},
}

# ── Demo channels ─────────────────────────────────────────────────────────────
DEMO_CHANNELS = {
    "C_PRODUCT":    {"name": "product",    "priority_category": "product"},
    "C_INCIDENTS":  {"name": "incidents",  "priority_category": "incidents"},
    "C_GENERAL":    {"name": "general",    "priority_category": "general"},
    "C_LEADERSHIP": {"name": "leadership", "priority_category": "leadership"},
    "C_OPS":        {"name": "ops",        "priority_category": "ops"},
}

# ── Demo messages (mentions + DMs) ────────────────────────────────────────────
DEMO_MESSAGES = [
    # --- Needs immediate reply ---
    {
        "msg_id":    "MSG_001",
        "sender_id": "U_RAHUL",
        "channel_id":"C_LEADERSHIP",
        "ts":        NOW - timedelta(hours=2, minutes=15),
        "text":      "Hey <@YOU>, quick one — can you share the Q3 product summary before the 4pm leadership call? Need it by 3:30.",
        "thread_ts": None,
        "is_dm":     False,
        "type":      "mention",
    },
    # --- Repeated question (answered many times before) ---
    {
        "msg_id":    "MSG_002",
        "sender_id": "U_SIDDHARTH",
        "channel_id":"C_GENERAL",
        "ts":        NOW - timedelta(hours=1, minutes=5),
        "text":      "Hi <@YOU>, where can I find the access request form for the analytics dashboard?",
        "thread_ts": None,
        "is_dm":     False,
        "type":      "mention",
    },
    # --- Incident channel ---
    {
        "msg_id":    "MSG_003",
        "sender_id": "U_VIKRAM",
        "channel_id":"C_INCIDENTS",
        "ts":        NOW - timedelta(minutes=25),
        "text":      "<@YOU> we have a P0 — payout job failed for 3 merchants. Need your sign-off to trigger manual retry. Blocker.",
        "thread_ts": None,
        "is_dm":     False,
        "type":      "mention",
    },
    # --- DM, low urgency ---
    {
        "msg_id":    "MSG_004",
        "sender_id": "U_PRIYA",
        "channel_id":"DM",
        "ts":        NOW - timedelta(hours=3),
        "text":      "Hey, can you review the updated onboarding doc when you get a chance? No rush, just flagging.",
        "thread_ts": None,
        "is_dm":     True,
        "type":      "dm",
    },
    # --- Follow-up owed by you ---
    {
        "msg_id":    "MSG_005",
        "sender_id": "U_ANANYA",
        "channel_id":"C_PRODUCT",
        "ts":        NOW - timedelta(days=1, hours=2),
        "text":      "Hey <@YOU>, following up on the campaign metrics you said you'd share yesterday. Still waiting!",
        "thread_ts": None,
        "is_dm":     False,
        "type":      "mention",
    },
    # --- Thread you're in, new message ---
    {
        "msg_id":    "MSG_006",
        "sender_id": "U_NEHA",
        "channel_id":"C_PRODUCT",
        "ts":        NOW - timedelta(minutes=45),
        "text":      "Looping in <@YOU> — we need a call on the roadmap prioritisation before Thursday. What slots work?",
        "thread_ts": "T_ROADMAP_THREAD",
        "is_dm":     False,
        "type":      "mention",
    },
    # --- External partner question ---
    {
        "msg_id":    "MSG_007",
        "sender_id": "U_ARJUN",
        "channel_id":"C_OPS",
        "ts":        NOW - timedelta(hours=4),
        "text":      "Hi <@YOU>, our team is asking about the integration timeline. Do you have an ETA?",
        "thread_ts": None,
        "is_dm":     False,
        "type":      "mention",
    },
    # --- Standard repeated question ---
    {
        "msg_id":    "MSG_008",
        "sender_id": "U_VIKRAM",
        "channel_id":"C_GENERAL",
        "ts":        NOW - timedelta(hours=1, minutes=30),
        "text":      "<@YOU> what's the process for raising a new feature request? Is there a template?",
        "thread_ts": None,
        "is_dm":     False,
        "type":      "mention",
    },
]

# ── Demo reply memory (past replies you've given) ─────────────────────────────
# In production this is built from actual Slack history.
# Here it's seeded with realistic examples.
DEMO_REPLY_MEMORY = [
    {
        "memory_id":   "MEM_001",
        "question_pattern": "access request form analytics dashboard",
        "canonical_reply":  "Hey! Here's the access request form: [DEMO_LINK]. Fill in your team and role, and it usually gets approved within a business day. Let me know if you run into issues.",
        "times_used":  9,
        "last_used":   "2024-10-28",
        "confidence":  "HIGH",
    },
    {
        "memory_id":   "MEM_002",
        "question_pattern": "feature request process template",
        "canonical_reply":  "We use the product backlog form for feature requests — it's in the team Notion under Product > Backlog. Add your request there and tag me so I can prioritise it in the next sprint planning.",
        "times_used":  7,
        "last_used":   "2024-10-30",
        "confidence":  "HIGH",
    },
    {
        "memory_id":   "MEM_003",
        "question_pattern": "availability slots calendar meeting",
        "canonical_reply":  "You can check my calendar directly — it's shared with the team. Feel free to block a slot that works. I'm generally free Tuesday/Thursday afternoons.",
        "times_used":  4,
        "last_used":   "2024-11-01",
        "confidence":  "MEDIUM",
    },
    {
        "memory_id":   "MEM_004",
        "question_pattern": "standup format daily update process",
        "canonical_reply":  "Standup is async in #daily-updates. Format: Yesterday / Today / Blockers. Post by 10am. No need for a call unless there's a blocker.",
        "times_used":  6,
        "last_used":   "2024-10-25",
        "confidence":  "HIGH",
    },
    {
        "memory_id":   "MEM_005",
        "question_pattern": "integration timeline ETA partner",
        "canonical_reply":  "Our current target for the integration is [DATE]. I'll send a more formal update once the engineering estimate is confirmed — should have that by end of week.",
        "times_used":  2,
        "last_used":   "2024-10-15",
        "confidence":  "MEDIUM",
    },
]
