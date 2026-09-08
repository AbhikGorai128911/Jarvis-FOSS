import sqlite3


DB_PATH = "memory/conversations.db"


def initialize():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)



    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            speaker TEXT,
            message TEXT
        )
    """)

    conn.commit()
    conn.close()


def remember(key, value):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO memories
        (key, value)
        VALUES (?, ?)
        """,
        (key, value)
    )

    conn.commit()
    conn.close()


def recall(key):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT value
        FROM memories
        WHERE key = ?
        """,
        (key,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None





def save_message(speaker, message):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO history
        (timestamp, speaker, message)
        VALUES (datetime('now'), ?, ?)
        """,
        (speaker, message)
    )

    conn.commit()
    conn.close()



def get_recent_messages(limit=10):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT speaker, message
        FROM history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows