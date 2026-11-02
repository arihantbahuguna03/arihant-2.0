"""
Arihant 2.0 — Slack Reader
=============================
Fetches messages where you were mentioned or received a DM.
In production: uses Slack Web API with a bot token.
In demo mode: returns synthetic messages from demo_data.py.

Production setup (not run in demo):
  1. Create a Slack app at api.slack.com/apps
  2. Add OAuth scopes: channels:history, im:history, users:read
  3. Install to workspace, copy Bot User OAuth Token
  4. Set SLACK_BOT_TOKEN env var

The reader normalises all messages into a standard dict shape
that the rest of the pipeline works with.
"""

import os
from datetime import datetime

from config import DEMO_MODE
from demo_data import DEMO_CHANNELS, DEMO_MESSAGES, DEMO_SENDERS


# ── Normalise a raw Slack API event into pipeline format ─────────────────────

def normalise_message(raw: dict) -> dict:
    return {
        "msg_id":          raw.get("msg_id", raw.get("ts", "")),
        "sender_id":       raw.get("sender_id", raw.get("user", "")),
        "sender_display":  DEMO_SENDERS.get(raw.get("sender_id",""), {}).get("display", raw.get("sender_id","")),
        "channel_id":      raw.get("channel_id", raw.get("channel", "")),
        "channel_name":    DEMO_CHANNELS.get(raw.get("channel_id",""), {}).get("name", "dm"),
        "ts":              raw.get("ts") if isinstance(raw.get("ts"), datetime) else datetime.now(),
        "text":            raw.get("text", ""),
        "thread_ts":       raw.get("thread_ts"),
        "is_dm":           raw.get("is_dm", False),
        "type":            raw.get("type", "mention"),
        # These get filled in by classifier.py
        "classification":  None,
        "core_question":   None,
        "urgency":         None,
        "context_summary": None,
    }


# ── Demo reader ───────────────────────────────────────────────────────────────

def fetch_demo_messages() -> list[dict]:
    return [normalise_message(m) for m in DEMO_MESSAGES]


# ── Production reader (Slack API) ─────────────────────────────────────────────

def fetch_live_messages(since_ts: datetime | None = None) -> list[dict]:
    """
    Fetch real messages from Slack API.
    Requires SLACK_BOT_TOKEN env var.
    """
    try:
        from slack_sdk import WebClient
    except ImportError:
        raise RuntimeError("slack_sdk not installed. Run: pip install slack-sdk")

    token  = os.environ["SLACK_BOT_TOKEN"]
    client = WebClient(token=token)

    # Get bot's own user ID
    bot_user_id = client.auth_test()["user_id"]

    messages = []
    oldest = str(since_ts.timestamp()) if since_ts else None

    # Fetch DMs
    dms = client.conversations_list(types="im")
    for dm in dms["channels"]:
        history = client.conversations_history(
            channel=dm["id"],
            oldest=oldest,
        )
        for msg in history["messages"]:
            messages.append(normalise_message({
                **msg,
                "channel_id": dm["id"],
                "is_dm":      True,
                "type":       "dm",
            }))

    # Fetch mentions in public/private channels
    search = client.search_messages(query=f"<@{bot_user_id}>")
    for match in search.get("messages", {}).get("matches", []):
        messages.append(normalise_message({
            **match,
            "sender_id":  match.get("user"),
            "channel_id": match.get("channel", {}).get("id"),
            "is_dm":      False,
            "type":       "mention",
        }))

    return messages


# ── Public interface ──────────────────────────────────────────────────────────

def fetch_messages(since_ts: datetime | None = None) -> list[dict]:
    if DEMO_MODE:
        return fetch_demo_messages()
    return fetch_live_messages(since_ts)
