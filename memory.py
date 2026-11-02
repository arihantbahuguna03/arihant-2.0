"""
Arihant 2.0 — Reply Memory Engine
====================================
Stores past replies, matches incoming questions to memory,
and returns a confidence-graded recommendation.

Every time a reply is sent (auto or manual), the memory grows.
Every time you correct a suggestion, the confidence of that pattern drops.
The longer you use it, the smarter it gets.

Storage: SQLite (local). In production, swap for a vector DB
(Pinecone, Weaviate) for semantic search at scale.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from config import (
    CONFIDENCE_HIGH_MIN_REPLIES,
    CONFIDENCE_MEDIUM_MIN_REPLIES,
    SIMILARITY_THRESHOLD,
)


DB_PATH = Path("/tmp/arihant_2_memory.db")


# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS reply_memory (
    memory_id         TEXT PRIMARY KEY,
    question_pattern  TEXT NOT NULL,
    canonical_reply   TEXT NOT NULL,
    times_used        INTEGER DEFAULT 1,
    times_corrected   INTEGER DEFAULT 0,
    last_used         TEXT,
    created_at        TEXT
);

CREATE TABLE IF NOT EXISTS reply_log (
    log_id       TEXT PRIMARY KEY,
    msg_id       TEXT,
    memory_id    TEXT,
    action       TEXT,  -- auto_replied / approved / corrected / skipped
    actual_reply TEXT,
    ts           TEXT
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


# ── Seed demo memory ──────────────────────────────────────────────────────────

def seed_demo_memory() -> None:
    from demo_data import DEMO_REPLY_MEMORY
    conn = get_conn()
    for m in DEMO_REPLY_MEMORY:
        existing = conn.execute(
            "SELECT memory_id FROM reply_memory WHERE memory_id = ?", (m["memory_id"],)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO reply_memory VALUES (?,?,?,?,?,?,?)",
                (
                    m["memory_id"],
                    m["question_pattern"],
                    m["canonical_reply"],
                    m["times_used"],
                    0,
                    m["last_used"],
                    datetime.now().isoformat(),
                ),
            )
    conn.commit()
    conn.close()


# ── Simple keyword overlap similarity (no vector DB needed for demo) ───────────

def _keyword_similarity(text_a: str, text_b: str) -> float:
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    stopwords = {"the","a","an","is","are","was","were","i","you","we","he","she","it",
                 "my","your","our","can","could","would","should","will","just","hey",
                 "hi","hello","please","thanks","thank","to","of","for","in","on","at"}
    words_a -= stopwords
    words_b -= stopwords
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    return len(intersection) / max(len(words_a), len(words_b))


# ── Core: find best memory match ──────────────────────────────────────────────

def find_match(question: str) -> dict | None:
    """
    Find the best matching memory entry for a given question.
    Returns the entry with confidence grade, or None if no match above threshold.
    """
    conn = get_conn()
    rows = conn.execute("SELECT * FROM reply_memory").fetchall()
    conn.close()

    best_score  = 0.0
    best_row    = None

    for row in rows:
        score = _keyword_similarity(question, row["question_pattern"])
        if score > best_score:
            best_score = score
            best_row   = row

    if best_score < SIMILARITY_THRESHOLD or best_row is None:
        return None

    times_used     = best_row["times_used"]
    times_corrected = best_row["times_corrected"]

    # Confidence degrades with corrections
    effective_uses = times_used - (times_corrected * 2)

    if effective_uses >= CONFIDENCE_HIGH_MIN_REPLIES:
        confidence = "HIGH"
    elif effective_uses >= CONFIDENCE_MEDIUM_MIN_REPLIES:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "memory_id":       best_row["memory_id"],
        "canonical_reply": best_row["canonical_reply"],
        "times_used":      times_used,
        "times_corrected": times_corrected,
        "confidence":      confidence,
        "similarity":      round(best_score, 3),
    }


# ── Update memory after a reply ───────────────────────────────────────────────

def record_reply(msg_id: str, memory_id: str | None, action: str, actual_reply: str) -> None:
    """
    action: 'auto_replied' | 'approved' | 'corrected' | 'skipped' | 'new'
    """
    import uuid
    conn = get_conn()

    conn.execute(
        "INSERT INTO reply_log VALUES (?,?,?,?,?,?)",
        (str(uuid.uuid4()), msg_id, memory_id, action, actual_reply, datetime.now().isoformat()),
    )

    if memory_id:
        if action in ("auto_replied", "approved"):
            conn.execute(
                "UPDATE reply_memory SET times_used = times_used + 1, last_used = ? WHERE memory_id = ?",
                (datetime.now().date().isoformat(), memory_id),
            )
        elif action == "corrected":
            conn.execute(
                "UPDATE reply_memory SET times_corrected = times_corrected + 1 WHERE memory_id = ?",
                (memory_id,),
            )

    conn.commit()
    conn.close()


def add_new_memory(question_pattern: str, reply: str) -> str:
    """Add a brand-new pattern to memory from a reply you just gave."""
    import uuid
    memory_id = f"MEM_{uuid.uuid4().hex[:8].upper()}"
    conn = get_conn()
    conn.execute(
        "INSERT INTO reply_memory VALUES (?,?,?,?,?,?,?)",
        (memory_id, question_pattern, reply, 1, 0, datetime.now().date().isoformat(), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    return memory_id
