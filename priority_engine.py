"""
Arihant 2.0 — Priority Engine
================================
Scores every open message across 5 dimensions and returns
a ranked list with priority labels and reasoning.

Priority levels:
  P0 — Act now (30 min SLA)
  P1 — Act today (4h SLA)
  P2 — Act this week
  P3 — FYI / no action needed
"""

from datetime import datetime

from config import (
    AGE_ESCALATION,
    CHANNEL_PRIORITIES,
    PRIORITY_WEIGHTS,
    SENDER_LEVELS,
    URGENCY_KEYWORDS,
)
from demo_data import DEMO_CHANNELS, DEMO_SENDERS


# ── Individual dimension scorers ──────────────────────────────────────────────

def score_sender(sender_id: str) -> tuple[int, str]:
    sender = DEMO_SENDERS.get(sender_id, {})
    level  = sender.get("level", "unknown")
    score  = SENDER_LEVELS.get(level, 2)
    return score, level


def score_urgency(text: str) -> tuple[int, list[str]]:
    text_lower = text.lower()
    total      = 0
    matched    = []
    for keyword, pts in URGENCY_KEYWORDS.items():
        if keyword in text_lower:
            total += pts
            matched.append(keyword)
    return min(total, 10), matched


def score_age(ts: datetime, now: datetime | None = None) -> tuple[int, int]:
    now     = now or datetime.now()
    minutes = int((now - ts).total_seconds() / 60)
    for threshold, pts in AGE_ESCALATION:
        if minutes >= threshold:
            return pts, minutes
    return 0, minutes


def score_channel(channel_id: str) -> tuple[int, str]:
    channel  = DEMO_CHANNELS.get(channel_id, {})
    category = channel.get("priority_category", "general")
    score    = CHANNEL_PRIORITIES.get(category, 3)
    return score, category


# ── Composite score ───────────────────────────────────────────────────────────

def compute_priority_score(msg: dict, now: datetime | None = None) -> dict:
    now = now or datetime.now()

    sender_score,  sender_level      = score_sender(msg["sender_id"])
    urgency_score, urgency_signals   = score_urgency(msg["text"])
    age_score,     age_minutes       = score_age(msg["ts"], now)
    channel_score, channel_category  = score_channel(msg.get("channel_id", ""))
    project_score                    = 5  # default; in production, look up project phase

    # Weighted composite (0–100)
    w = PRIORITY_WEIGHTS
    raw = (
        sender_score  / 10 * w["sender_level"]     +
        urgency_score / 10 * w["urgency_language"]  +
        age_score     / 10 * w["age_minutes"]       +
        channel_score / 10 * w["channel_context"]   +
        project_score / 10 * w["project_phase"]
    )

    # Priority label
    if raw >= 70:
        label = "P0"
        sla   = "Act now"
    elif raw >= 45:
        label = "P1"
        sla   = "Act today"
    elif raw >= 20:
        label = "P2"
        sla   = "Act this week"
    else:
        label = "P3"
        sla   = "FYI"

    # Build reasoning string
    reasons = []
    if sender_level in ("founder", "vp", "director"):
        reasons.append(f"senior sender ({sender_level})")
    if urgency_signals:
        reasons.append(f"urgency keywords: {', '.join(urgency_signals[:2])}")
    if age_minutes >= 120:
        reasons.append(f"waiting {age_minutes//60}h {age_minutes%60}m")
    if channel_category in ("incidents", "leadership"):
        reasons.append(f"high-priority channel (#{channel_category})")

    return {
        **msg,
        "priority_score": round(raw, 1),
        "priority_label": label,
        "priority_sla":   sla,
        "priority_reason": "; ".join(reasons) if reasons else "standard",
        "age_minutes":    age_minutes,
    }


def rank_messages(messages: list[dict], now: datetime | None = None) -> list[dict]:
    scored = [compute_priority_score(m, now) for m in messages]
    scored.sort(key=lambda x: x["priority_score"], reverse=True)
    return scored
