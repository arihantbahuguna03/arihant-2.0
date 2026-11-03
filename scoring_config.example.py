"""
Arihant 2.0 — Scoring Config Example
=======================================
Copy this file to scoring_config.py and fill in your calibrated values.
scoring_config.py is gitignored — this example shows the structure only.

Values were calibrated by running the bot on real Slack data over several
months and tuning until reply priority matched actual urgency in practice.
"""

# ── Priority scoring weights (must sum to 100) ────────────────────────────────
# Calibration: proprietary — available on request.
PRIORITY_WEIGHTS = {
    "sender_level":     None,   # how much sender seniority contributes
    "urgency_language": None,   # how much urgency keywords contribute
    "age_minutes":      None,   # how much waiting time contributes
    "channel_context":  None,   # how much channel type contributes
    "project_phase":    None,   # how much project phase contributes
}

# ── Sender level scores ───────────────────────────────────────────────────────
SENDER_LEVELS = {
    "founder":       None,
    "vp":            None,
    "director":      None,
    "direct_report": None,
    "peer":          None,
    "external":      None,
    "unknown":       None,
}

# ── Urgency keyword scores ────────────────────────────────────────────────────
# Calibration: proprietary — available on request.
URGENCY_KEYWORDS = {
    # "keyword": score (0–10)
    # e.g. "p0": 10, "blocker": 8, "urgent": 7
}

# ── Channel priority scores ───────────────────────────────────────────────────
CHANNEL_PRIORITIES = {
    # "channel_type": score (0–10)
    # e.g. "incidents": 10, "leadership": 8
}

# ── Age escalation table [(minutes_threshold, priority_bonus), ...] ──────────
AGE_ESCALATION = [
    # (minutes_unreplied, priority_bonus)
    # e.g. (240, 10), (120, 7), (60, 4), (30, 2), (0, 0)
]

# ── Similarity and confidence thresholds ─────────────────────────────────────
SIMILARITY_THRESHOLD          = None   # 0–1 cosine similarity for reply memory match
CONFIDENCE_HIGH_MIN_REPLIES   = None   # N past replies → auto-reply
CONFIDENCE_MEDIUM_MIN_REPLIES = None   # N past replies → suggest + confirm

# ── Skill triggers ────────────────────────────────────────────────────────────
# Maps question patterns to callable skill names.
# Not included — skill names and patterns reveal the company's data surfaces.
SKILL_TRIGGERS = [
    # {
    #     "patterns": ["keyword1", "keyword2"],
    #     "skill":    "skill_function_name",
    #     "description": "What this skill does",
    # },
]
