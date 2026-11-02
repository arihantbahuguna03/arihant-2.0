"""
Arihant 2.0 — Skill Trigger System
=====================================
Detects when an incoming message matches a known automatable pattern
and runs the corresponding skill — returning the live answer instead of
a drafted reply.

Example:
  "What's the current success rate?" →
  → matches skill: query_success_rate
  → runs skill → returns live metrics
  → auto-replies with data, not a template

Skills are Python functions registered in SKILL_REGISTRY.
In production, skills connect to real data sources (ClickHouse, APIs, etc).
Demo skills return synthetic data.
"""

from config import SKILL_TRIGGERS


# ── Skill registry ────────────────────────────────────────────────────────────

def query_success_rate(**kwargs) -> str:
    """Demo skill: returns a fake payment success rate summary."""
    return (
        "Current payment success rate: 94.2% (last 1h). "
        "Breakdown by method: Card 93.8%, UPI 96.1%, Wallet 91.4%. "
        "No active incidents. Last updated: just now."
    )


def creator_onboarding_status(**kwargs) -> str:
    """Demo skill: returns creator funnel status."""
    return (
        "Creator onboarding this week: 48 signups → 38 profile complete (79%) → "
        "21 first post (55% of completers). "
        "3 creators stuck at brief step for >24h — flagged for nudge."
    )


def campaign_status(**kwargs) -> str:
    """Demo skill: returns active campaign summary."""
    return (
        "3 active campaigns: Demo Cafe (live, 4.2K reach), "
        "Demo Fitness Studio (awaiting creator confirmation), "
        "Demo Home Decor (completed, report sent). "
        "1 campaign pending your approval before going live."
    )


SKILL_REGISTRY = {
    "query_success_rate":       query_success_rate,
    "creator_onboarding_status": creator_onboarding_status,
    "campaign_status":          campaign_status,
}


# ── Trigger detection ─────────────────────────────────────────────────────────

def detect_skill_trigger(text: str) -> dict | None:
    """
    Check if a message text matches any skill trigger pattern.
    Returns the matched skill config or None.
    """
    text_lower = text.lower()
    for trigger in SKILL_TRIGGERS:
        if any(pattern in text_lower for pattern in trigger["patterns"]):
            return trigger
    return None


def run_skill(skill_name: str, **kwargs) -> str | None:
    fn = SKILL_REGISTRY.get(skill_name)
    if not fn:
        return None
    return fn(**kwargs)


def try_skill_reply(msg: dict) -> dict | None:
    """
    If the message matches a skill trigger, run the skill and return
    a ready-to-send auto-reply dict. Otherwise return None.
    """
    question = msg.get("core_question") or msg["text"]
    trigger  = detect_skill_trigger(question)

    if not trigger:
        return None

    result = run_skill(trigger["skill"])
    if not result:
        return None

    print(f"  ⚡ SKILL TRIGGERED: {trigger['skill']}")
    print(f"     Result: {result[:80]}…")

    return {
        "msg_id":     msg["msg_id"],
        "action":     "skill_auto_replied",
        "skill_used": trigger["skill"],
        "reply_sent": result,
        "confidence": "SKILL",
    }
