"""
Arihant 2.0 — Twice-Daily Digest Generator
=============================================
Runs at 12:00 and 19:00. Reads the full open-items list,
groups by priority, and uses Claude to write a sharp,
actionable brief — not a notification dump.

The digest covers:
  🔴 Needs you now (P0)
  🟡 Reply when you can (P1)
  ⬜ FYI / no action (P2/P3)
  ✅ Auto-replied today (done by the bot)
  ⏰ Follow-ups you owe (you said you'd do something)
"""

from datetime import datetime

import anthropic

from config import YOUR_NAME
from demo_data import DEMO_CHANNELS, DEMO_SENDERS
from priority_engine import rank_messages


# ── Format helpers ────────────────────────────────────────────────────────────

def _sender_name(sender_id: str) -> str:
    return DEMO_SENDERS.get(sender_id, {}).get("display", sender_id)


def _channel_name(channel_id: str) -> str:
    return DEMO_CHANNELS.get(channel_id, {}).get("name", channel_id)


def _age_str(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m ago"
    h = minutes // 60
    m = minutes % 60
    return f"{h}h {m}m ago" if m else f"{h}h ago"


# ── Claude digest writer ──────────────────────────────────────────────────────

def generate_digest(
    open_messages:    list[dict],
    auto_replied:     list[dict],
    follow_ups_owed:  list[dict],
    period:           str = "mid-day",
) -> str:
    client = anthropic.Anthropic()

    ranked = rank_messages(open_messages)
    now    = datetime.now()

    open_text = "\n".join(
        f"  [{m['priority_label']}] {_sender_name(m['sender_id'])} in "
        f"#{_channel_name(m.get('channel_id',''))} — "
        f"\"{m.get('core_question', m['text'][:50])}\" "
        f"({_age_str(m.get('age_minutes', 0))}) | reason: {m.get('priority_reason','')}"
        for m in ranked
    ) or "  (none)"

    auto_text = "\n".join(
        f"  • {r.get('sender','?')} — auto-replied ({r.get('confidence','')})"
        for r in auto_replied
    ) or "  (none)"

    fu_text = "\n".join(
        f"  • {_sender_name(m['sender_id'])} — \"{m.get('core_question', m['text'][:50])}\""
        for m in follow_ups_owed
    ) or "  (none)"

    prompt = f"""You are {YOUR_NAME}'s AI chief of staff. Write a sharp, actionable {period} brief for {YOUR_NAME}.

Open items (ranked by priority):
{open_text}

Auto-replied today by the bot:
{auto_text}

Follow-ups {YOUR_NAME} owes:
{fu_text}

Write a digest in this exact format:
1. A one-line situation summary (e.g. "3 items need you before EOD, 1 is a P0")
2. A numbered list of open items with: priority label, who it's from, what they need, how long it's been waiting
3. A short "your 3 actions right now" section — the most important things to do next
4. A brief note on what the bot handled automatically

Keep it under 250 words. Be direct. No filler. Write as if briefing a busy person who has 60 seconds."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ── Main digest runner ────────────────────────────────────────────────────────

def run_digest(
    all_messages:   list[dict],
    auto_replied:   list[dict],
    period:         str = "mid-day",
) -> str:
    now = datetime.now()

    open_messages   = [m for m in all_messages if m.get("classification") != "fyi"]
    follow_ups_owed = [m for m in all_messages if m.get("classification") == "follow_up_owed"]

    print(f"\n{'='*65}")
    print(f"  ARIHANT 2.0 — {period.upper()} BRIEF | {now.strftime('%b %d, %Y %H:%M')}")
    print(f"{'='*65}\n")

    digest = generate_digest(open_messages, auto_replied, follow_ups_owed, period)
    print(digest)
    print()

    return digest
