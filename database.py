import sqlite3
from config import DB_FILE


def connect_db():

    DB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(DB_FILE)

    conn.row_factory = sqlite3.Row

    return conn


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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'pending',
            group_id TEXT,
            error TEXT,
            sent_at DATETIME,
            FOREIGN KEY (post_id) REFERENCES posts(id)
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

                if initialized is not None:

                    conn.execute("""
                        INSERT OR IGNORE INTO notifications
                        (post_id, status)
                        VALUES (?, 'pending')
                    """, (post["id"],))

        conn.execute("""
            INSERT OR IGNORE INTO settings
            (key, value)
            VALUES ('initialized', 'true')
        """)

        conn.commit()

        if initialized is None:

            print("Initial database setup completed.")

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


def get_pending_notifications():

    conn = connect_db()

    rows = conn.execute("""
        SELECT posts.*
        FROM posts
        JOIN notifications
        ON posts.id = notifications.post_id
        WHERE notifications.status = 'pending'
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def claim_notification(post_id):

    conn = connect_db()

    cursor = conn.execute("""
        UPDATE notifications
        SET status = 'sending'
        WHERE post_id = ?
        AND status = 'pending'
    """, (post_id,))

    conn.commit()

    claimed = cursor.rowcount == 1

    conn.close()

    return claimed


def mark_accepted(post_id, group_id):

    conn = connect_db()

    conn.execute("""
        UPDATE notifications
        SET status = 'accepted',
            group_id = ?,
            sent_at = CURRENT_TIMESTAMP,
            error = NULL
        WHERE post_id = ?
    """, (group_id, post_id))

    conn.commit()
    conn.close()


def mark_failed(post_id, error, status="failed"):

    conn = connect_db()

    conn.execute("""
        UPDATE notifications
        SET status = ?,
            error = ?
        WHERE post_id = ?
    """, (status, error, post_id))

    conn.commit()
    conn.close()