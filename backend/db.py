"""طبقة قاعدة البيانات: كل التعامل مع MySQL موجود هنا."""
import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def _run(query, params=(), fetch=False):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def save_analysis(text, sentiment, confidence):
    return _run(
        "INSERT INTO analyses (text, sentiment, confidence) VALUES (%s, %s, %s)",
        (text, sentiment, confidence),
    )


def get_history(limit=20):
    rows = _run(
        "SELECT id, text, sentiment, confidence, created_at "
        "FROM analyses ORDER BY id DESC LIMIT %s",
        (limit,),
        fetch=True,
    )
    for r in rows:
        r["confidence"] = float(r["confidence"])
        r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M")
    return rows


def delete_analysis(analysis_id):
    _run("DELETE FROM analyses WHERE id = %s", (analysis_id,))


def get_stats():
    rows = _run(
        "SELECT sentiment, COUNT(*) AS total FROM analyses GROUP BY sentiment",
        fetch=True,
    )
    stats = {"positive": 0, "negative": 0, "neutral": 0}
    for r in rows:
        stats[r["sentiment"]] = r["total"]
    return stats


def add_training_example(text, label):
    _run("INSERT INTO training_data (text, label) VALUES (%s, %s)", (text, label))


def get_training_examples():
    rows = _run("SELECT text, label FROM training_data", fetch=True)
    return [(r["text"], r["label"]) for r in rows]
