"""
Arihant 2.0 — Reply Engine
=============================
Dispatches replies based on memory confidence:

  HIGH    → auto-reply on your behalf (or as "Arihant asked me to share")
  MEDIUM  → draft reply + send you a 1-tap approval request
  LOW/NEW → post "will get back to you" in the thread,
             send you the draft + recommended reply

All replies are logged. Corrections feed back into memory confidence.
"""

import anthropic

from config import HOLD_MESSAGE_TEMPLATE, YOUR_NAME
from memory import find_match, record_reply


# ── Draft a reply from scratch (when no memory match) ────────────────────────

def draft_reply_with_claude(msg: dict) -> str:
    client  = anthropic.Anthropic()
    sender  = msg.get("sender_display", "the person")

    prompt = f"""You are drafting a reply on behalf of {YOUR_NAME}, a product/growth lead at a startup.

Context:
- {sender} sent this message: "{msg.get('core_question', msg['text'])}"
- Channel: #{msg.get('channel_name', 'unknown')}
- Message type: {msg.get('classification', 'reply_required')}

Draft a professional, friendly reply in {YOUR_NAME}'s voice. Keep it under 3 sentences.
Be direct and helpful. Do not over-explain. If you need more context to give a specific answer,
say so briefly and say {YOUR_NAME} will follow up.

Return only the reply text, nothing else."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ── Main dispatch ─────────────────────────────────────────────────────────────

def dispatch_reply(msg: dict, dry_run: bool = True) -> dict:
    """
    Process one message through the reply engine.
    dry_run=True: print what would happen, don't actually send.

    Returns a result dict describing what was done / what needs your approval.
    """
    question = msg.get("core_question") or msg["text"]
    match    = find_match(question)

    sender_name = msg.get("sender_display", "Someone")
    msg_id      = msg["msg_id"]

    result = {
        "msg_id":     msg_id,
        "sender":     sender_name,
        "question":   question[:80],
        "action":     None,
        "reply_sent": None,
        "needs_your_input": False,
        "recommended_reply": None,
        "confidence": None,
        "memory_id":  None,
    }

    if match and match["confidence"] == "HIGH":
        # AUTO-REPLY
        reply = match["canonical_reply"]
        result.update({
            "action":     "auto_replied",
            "reply_sent": reply,
            "confidence": f"HIGH ({match['times_used']} past uses, similarity {match['similarity']})",
            "memory_id":  match["memory_id"],
        })
        if not dry_run:
            # In production: slack_client.chat_postMessage(channel=..., text=reply)
            record_reply(msg_id, match["memory_id"], "auto_replied", reply)
        print(f"  ✅ AUTO-REPLIED to {sender_name}")
        print(f"     Reply: {reply[:80]}…")

    elif match and match["confidence"] == "MEDIUM":
        # SUGGEST + AWAIT APPROVAL
        reply = match["canonical_reply"]
        result.update({
            "action":            "awaiting_approval",
            "recommended_reply": reply,
            "confidence":        f"MEDIUM ({match['times_used']} past uses)",
            "memory_id":         match["memory_id"],
            "needs_your_input":  True,
        })
        print(f"  🔶 SUGGEST TO YOU — {sender_name}")
        print(f"     Recommended reply: {reply[:80]}…")
        print(f"     [Approve / Edit / Skip]")

    else:
        # LOW / NO MATCH — hold message + draft for you
        hold_msg = HOLD_MESSAGE_TEMPLATE.format(name=sender_name.split()[0], your_name=YOUR_NAME)
        draft    = draft_reply_with_claude(msg)
        result.update({
            "action":            "held_with_draft",
            "reply_sent":        hold_msg,
            "recommended_reply": draft,
            "confidence":        "LOW" if match else "NEW (no memory match)",
            "needs_your_input":  True,
        })
        if not dry_run:
            # In production: post hold_msg to thread, then DM you the draft
            pass
        print(f"  ⬜ HOLDING + DRAFTING — {sender_name}")
        print(f"     Sent to thread: '{hold_msg}'")
        print(f"     Recommended reply for you: {draft[:80]}…")

    return result


def process_messages(messages: list[dict], dry_run: bool = True) -> list[dict]:
    results = []
    for msg in messages:
        print(f"\n[{msg['msg_id']}] {msg.get('sender_display','?')} → {msg.get('core_question','?')[:60]}")
        result = dispatch_reply(msg, dry_run=dry_run)
        results.append(result)
    return results
