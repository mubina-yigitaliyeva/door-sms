import sqlite3
from config import DB_FILE


def connect_db():

    DB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(DB_FILE)


def init_db():

    conn = connect_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            course TEXT,
            title TEXT NOT NULL,
            date TEXT,
            deadline TEXT,
            url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_posts(posts):

    conn = connect_db()

    new_posts = []

    try:

        initialized = conn.execute("""
            SELECT value FROM settings
            WHERE key = 'initialized'
        """).fetchone()

        for post in posts:

            cursor = conn.execute("""
                INSERT OR IGNORE INTO posts
                (id, type, course, title, date, deadline, url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                post["id"],
                post["type"],
                post.get("course"),
                post["title"],
                post.get("date"),
                post.get("deadline"),
                post.get("url")
            ))

            if cursor.rowcount == 1:
                new_posts.append(post)

        conn.execute("""
            INSERT OR IGNORE INTO settings
            (key, value)
            VALUES ('initialized', 'true')
        """)

        conn.commit()

        if initialized is None:
            print("Initial database setup completed.")
            print(f"Saved {len(new_posts)} existing posts.")
            return []

        return new_posts

    finally:

        conn.close()


def count_posts():

    conn = connect_db()

    count = conn.execute("""
        SELECT COUNT(*) FROM posts
    """).fetchone()[0]

    conn.close()

    return count