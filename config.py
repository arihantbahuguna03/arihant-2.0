"""
Arihant 2.0 — Configuration
=============================
All tunable thresholds, priority rules, and schedule settings.
Edit this file to personalise the bot's behaviour.
"""

# ── Digest schedule ───────────────────────────────────────────────────────────
DIGEST_TIMES = ["12:00", "19:00"]   # 24h, local time

# ── Confidence thresholds ─────────────────────────────────────────────────────
# How many past similar replies qualify as HIGH/MEDIUM confidence
CONFIDENCE_HIGH_MIN_REPLIES   = 5    # 5+ similar past replies → auto-reply
CONFIDENCE_MEDIUM_MIN_REPLIES = 2    # 2–4 → suggest + confirm
# Below 2 → LOW → "will get back to you" + recommend

# Semantic similarity threshold (0–1) for reply memory matching
SIMILARITY_THRESHOLD = 0.72

# ── Priority scoring weights ──────────────────────────────────────────────────
PRIORITY_WEIGHTS = {
    "sender_level":     30,   # founder/VP/direct-report/peer/external
    "urgency_language": 25,   # blocker, urgent, EOD, P0, production
    "age_minutes":      20,   # how long it's been waiting
    "channel_context":  15,   # incident > leadership > product > random
    "project_phase":    10,   # launch week > active > planning > archived
}

# Sender levels (higher = more priority points)
SENDER_LEVELS = {
    "founder":       10,
    "vp":             8,
    "director":       7,
    "direct_report":  6,
    "peer":           4,
    "external":       3,
    "unknown":        2,
}

# Urgency keywords and their scores
URGENCY_KEYWORDS = {
    "production down":  10,
    "p0":               10,
    "critical":          9,
    "blocker":           8,
    "urgent":            7,
    "eod":               6,
    "end of day":        6,
    "asap":              6,
    "deadline":          5,
    "stuck":             4,
    "waiting on you":    4,
    "need your input":   3,
}

# Channel priority scores
CHANNEL_PRIORITIES = {
    "incidents":     10,
    "alerts":         9,
    "leadership":     8,
    "product":        6,
    "engineering":    6,
    "ops":            5,
    "general":        3,
    "random":         1,
}

# Age escalation (minutes unreplied → priority bonus)
AGE_ESCALATION = [
    (240, 10),   # 4h+ → +10
    (120, 7),    # 2h+ → +7
    (60,  4),    # 1h+ → +4
    (30,  2),    # 30m+ → +2
    (0,   0),
]

# ── Auto-reply settings ───────────────────────────────────────────────────────
HOLD_MESSAGE_TEMPLATE = "Hey {name}, {your_name} will get back to you shortly!"
YOUR_NAME = "Arihant"

# ── Skill triggers ────────────────────────────────────────────────────────────
# Maps question patterns to skill names. Skills are callable functions
# registered in skill_triggers.py.
SKILL_TRIGGERS = [
    {
        "patterns": ["success rate", "sr", "payment sr", "conversion rate"],
        "skill":    "query_success_rate",
        "description": "Queries live payment success rate metrics",
    },
    {
        "patterns": ["onboarding status", "creator onboarding", "new creator"],
        "skill":    "creator_onboarding_status",
        "description": "Returns current creator onboarding funnel metrics",
    },
    {
        "patterns": ["campaign status", "deal status", "how is the campaign"],
        "skill":    "campaign_status",
        "description": "Returns current campaign performance summary",
    },
]

# ── Demo mode ─────────────────────────────────────────────────────────────────
DEMO_MODE = True   # When True, uses demo_data.py instead of live Slack API
