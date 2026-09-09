# database.py - handles persistent storage of conversation history using SQLite
# replaces the in-memory `conversations` dict so history survives server restarts

import sqlite3

DB_FILE = "rupert.db"


def init_db():
    # creates the messages table if it doesn't already exist
    # each row is one message; a full conversation is all rows sharing a conversation_id
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_message(conversation_id: str, role: str, content: str):
    # saves a single message to the database
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content),
    )
    conn.commit()
    conn.close()


def load_conversation(conversation_id: str) -> list[dict]:
    # rebuilds the message list for a given conversation, ordered by when each message was saved
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in rows]


def conversation_exists(conversation_id: str) -> bool:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute(
        "SELECT 1 FROM messages WHERE conversation_id = ? LIMIT 1",
        (conversation_id,),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists