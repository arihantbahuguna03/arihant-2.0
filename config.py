"""
Arihant 2.0 — Configuration
=============================
All tunable thresholds, priority rules, and schedule settings.
Edit this file to personalise the bot's behaviour.
"""

# ── Digest schedule ───────────────────────────────────────────────────────────
DIGEST_TIMES = ["12:00", "19:00"]   # 24h, local time

# ── Auto-reply settings ───────────────────────────────────────────────────────
HOLD_MESSAGE_TEMPLATE = "Hey {name}, {your_name} will get back to you shortly!"
YOUR_NAME = "Arihant"


# ── Calibrated scoring config (loaded from gitignored scoring_config.py) ──────

def _load_scoring_config():
    """
    Load calibrated priority weights, sender levels, urgency keywords,
    channel priorities, age escalation rules, similarity threshold,
    confidence thresholds, and skill triggers from scoring_config.py.

    Values were tuned over several months of real usage — they reflect
    the actual urgency distribution in a fast-moving startup Slack environment.
    Skill triggers also reveal the company's internal data surfaces.

    Implementation: proprietary — available on request.
    Copy scoring_config.example.py → scoring_config.py to run with your own values.
    """
    try:
        import scoring_config
        return (
            scoring_config.PRIORITY_WEIGHTS,
            scoring_config.SENDER_LEVELS,
            scoring_config.URGENCY_KEYWORDS,
            scoring_config.CHANNEL_PRIORITIES,
            scoring_config.AGE_ESCALATION,
            scoring_config.SIMILARITY_THRESHOLD,
            scoring_config.CONFIDENCE_HIGH_MIN_REPLIES,
            scoring_config.CONFIDENCE_MEDIUM_MIN_REPLIES,
            scoring_config.SKILL_TRIGGERS,
        )
    except ImportError:
        raise RuntimeError(
            "scoring_config.py not found. "
            "Copy scoring_config.example.py → scoring_config.py and fill in your values."
        )


(
    PRIORITY_WEIGHTS,
    SENDER_LEVELS,
    URGENCY_KEYWORDS,
    CHANNEL_PRIORITIES,
    AGE_ESCALATION,
    SIMILARITY_THRESHOLD,
    CONFIDENCE_HIGH_MIN_REPLIES,
    CONFIDENCE_MEDIUM_MIN_REPLIES,
    SKILL_TRIGGERS,
) = _load_scoring_config()

# ── Demo mode ─────────────────────────────────────────────────────────────────
DEMO_MODE = True   # When True, uses demo_data.py instead of live Slack API
