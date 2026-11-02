"""
Arihant 2.0 — Main Entry Point
================================
Runs the full pipeline:
  1. Fetch Slack messages (demo or live)
  2. Classify each message with Claude
  3. Check skill triggers first
  4. For non-skill messages: check reply memory + dispatch
  5. Score and rank all open items by priority
  6. Generate twice-daily digest

Run modes:
  python main.py              — full pipeline (demo mode)
  python main.py --digest     — generate digest only
  python main.py --live       — switch to live Slack API
  python main.py --dry-run    — show what would happen, don't send anything

This is meant to run on a schedule (cron or Airflow) at 12:00 and 19:00.
"""

import argparse
import sys
from datetime import datetime

from classifier import classify_with_claude
from config import DEMO_MODE, DIGEST_TIMES, YOUR_NAME
from digest import run_digest
from memory import seed_demo_memory
from priority_engine import rank_messages
from reply_engine import process_messages
from skill_triggers import try_skill_reply
from slack_reader import fetch_messages


def determine_period() -> str:
    hour = datetime.now().hour
    return "mid-day" if hour < 15 else "end of day"


def run_pipeline(dry_run: bool = True) -> None:
    print(f"\n{'='*65}")
    print(f"  ARIHANT 2.0 — Starting pipeline | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Mode: {'DEMO' if DEMO_MODE else 'LIVE'} | {'DRY RUN' if dry_run else 'LIVE SEND'}")
    print(f"{'='*65}\n")

    # 1. Seed demo memory on first run
    seed_demo_memory()

    # 2. Fetch messages
    print("📥 Fetching messages…")
    messages = fetch_messages()
    print(f"   {len(messages)} messages fetched\n")

    # 3. Classify with Claude
    print("🧠 Classifying messages…")
    messages = classify_with_claude(messages)

    # 4. Skill trigger check (fast path — before memory lookup)
    print("\n⚡ Checking skill triggers…")
    skill_handled = []
    remaining     = []
    for msg in messages:
        skill_result = try_skill_reply(msg)
        if skill_result:
            skill_handled.append(skill_result)
        else:
            remaining.append(msg)

    print(f"   {len(skill_handled)} message(s) handled by skills")
    print(f"   {len(remaining)} message(s) going to reply engine\n")

    # 5. Reply engine — memory match + dispatch
    print("💬 Running reply engine…")
    reply_results = process_messages(remaining, dry_run=dry_run)

    auto_replied  = [r for r in reply_results + skill_handled
                     if r.get("action") in ("auto_replied", "skill_auto_replied")]
    needs_your_input = [r for r in reply_results if r.get("needs_your_input")]

    # 6. Priority ranking of what still needs you
    open_msgs = [m for m in remaining
                 if any(r["msg_id"] == m["msg_id"] and r.get("needs_your_input")
                        for r in reply_results)]

    print(f"\n  ✅ Auto-handled: {len(auto_replied)}")
    print(f"  🔶 Needs your approval: {len([r for r in reply_results if r.get('action')=='awaiting_approval'])}")
    print(f"  ⬜ Needs your reply: {len([r for r in reply_results if r.get('action')=='held_with_draft'])}")

    # 7. Ranked open items
    if open_msgs:
        print("\n📊 Priority ranking of open items:")
        ranked = rank_messages(open_msgs)
        for m in ranked:
            print(f"  [{m['priority_label']}] {m.get('sender_display','?')} — "
                  f"{m.get('core_question','?')[:50]} | {m.get('priority_reason','')}")

    # 8. Generate digest
    print(f"\n📋 Generating {determine_period()} digest…\n")
    run_digest(remaining, auto_replied, period=determine_period())

    # 9. Items needing your input — send as DM/notification in production
    if needs_your_input:
        print(f"\n🔔 ITEMS WAITING FOR YOUR INPUT ({len(needs_your_input)}):")
        for r in needs_your_input:
            print(f"\n  [{r['msg_id']}] From: {r['sender']}")
            print(f"  Question: {r['question']}")
            if r.get("recommended_reply"):
                print(f"  Recommended reply: {r['recommended_reply'][:120]}…")
            if r.get("confidence"):
                print(f"  Confidence: {r['confidence']}")


def run_digest_only() -> None:
    seed_demo_memory()
    messages = fetch_messages()
    messages = classify_with_claude(messages)
    run_digest(messages, [], period=determine_period())


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arihant 2.0 — Your AI Chief of Staff")
    parser.add_argument("--digest",  action="store_true", help="Generate digest only")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Don't send actual replies")
    parser.add_argument("--live",    action="store_true", help="Use live Slack API (requires SLACK_BOT_TOKEN)")
    args = parser.parse_args()

    if args.live:
        import config
        config.DEMO_MODE = False

    if args.digest:
        run_digest_only()
    else:
        run_pipeline(dry_run=not args.live)
