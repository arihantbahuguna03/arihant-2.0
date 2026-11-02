"""
Arihant 2.0 — Message Classifier
===================================
Classifies incoming Slack messages into action types and
extracts the core question / request for memory matching.

Classification types:
  - action_required   : you need to do something specific
  - reply_required    : someone asked you something
  - fyi               : informational, no action needed
  - follow_up_owed    : you previously said you'd do something
  - thread_update     : new message in a thread you're part of

Uses Claude for nuanced cases. Falls back to rule-based for speed.
"""

import re
from datetime import datetime

import anthropic

from config import YOUR_NAME


# ── Rule-based fast classifier ────────────────────────────────────────────────

QUESTION_SIGNALS   = ["?", "can you", "could you", "do you", "would you",
                      "can i", "how do", "what is", "what's", "where is",
                      "where can", "when is", "which", "who is"]

ACTION_SIGNALS     = ["please", "sign off", "approve", "review", "sign-off",
                      "need your", "waiting on you", "blocker", "urgent",
                      "p0", "asap", "eod", "end of day"]

FOLLOW_UP_SIGNALS  = ["following up", "following-up", "circling back",
                      "gentle reminder", "still waiting", "any update",
                      "you mentioned", "you said you'd"]

FYI_SIGNALS        = ["fyi", "heads up", "for your awareness", "just letting you know",
                      "no action needed", "just flagging"]


def fast_classify(text: str) -> str:
    text_lower = text.lower()

    if any(s in text_lower for s in FOLLOW_UP_SIGNALS):
        return "follow_up_owed"
    if any(s in text_lower for s in FYI_SIGNALS):
        return "fyi"
    if any(s in text_lower for s in ACTION_SIGNALS):
        return "action_required"
    if any(s in text_lower for s in QUESTION_SIGNALS):
        return "reply_required"
    return "reply_required"  # default: assume a reply is needed


def extract_core_question(text: str) -> str:
    """Strip Slack formatting and pull out the core ask."""
    # Remove @mentions
    text = re.sub(r"<@\w+>", "", text)
    # Remove Slack formatting
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return text.strip()


# ── Claude-powered deep classifier ────────────────────────────────────────────

def classify_with_claude(messages: list[dict]) -> list[dict]:
    """
    For a batch of messages, use Claude to:
    1. Classify each message type
    2. Extract the core question/request
    3. Identify if this is a skill-triggerable question
    """
    client = anthropic.Anthropic()

    batch_text = "\n\n".join(
        f"[MSG_{i+1}] From: {m['sender_id']} | Channel: {m['channel_id']}\n"
        f"Time: {m['ts'].strftime('%H:%M')}\n"
        f"Text: {extract_core_question(m['text'])}"
        for i, m in enumerate(messages)
    )

    prompt = f"""You are classifying Slack messages for {YOUR_NAME}'s personal assistant.

For each message, return JSON with:
- msg_index: (1-based)
- classification: one of [action_required, reply_required, fyi, follow_up_owed, thread_update]
- core_question: the key thing being asked/requested, in 10 words or less
- urgency: high / medium / low
- context_summary: one sentence describing what this is about

Messages:
{batch_text}

Return a JSON array of objects, one per message. No extra text."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    classifications = json.loads(raw)

    for i, clf in enumerate(classifications):
        if i < len(messages):
            messages[i]["classification"]  = clf.get("classification", "reply_required")
            messages[i]["core_question"]   = clf.get("core_question", "")
            messages[i]["urgency"]         = clf.get("urgency", "medium")
            messages[i]["context_summary"] = clf.get("context_summary", "")

    return messages
