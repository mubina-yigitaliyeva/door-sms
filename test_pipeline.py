from database import init_db, save_posts
from main import process_notifications
from config import DOOR_URL


def test_pipeline():

    init_db()

    test_post = {
        "id": "test_notice_001",
        "type": "notice",
        "course": "Web Programming II",
        "title": "Test Announcement",
        "date": "2026-11-24",
        "url": DOOR_URL
    }

    new_posts = save_posts([test_post])

    print("New posts detected:", len(new_posts))

    process_notifications()


if __name__ == "__main__":
    test_pipeline()