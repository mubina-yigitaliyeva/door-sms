import os

from dotenv import load_dotenv

from scraper import scrape_assignments, scrape_posts

from database import (
    init_db,
    save_posts,
    count_posts,
    get_pending_notifications,
    claim_notification,
    mark_accepted,
    mark_failed
)

from notifier import send_notification
from config import DOOR_URL

load_dotenv()


def process_notifications():

    enabled = os.getenv(
        "SMS_ENABLED", "false"
    ).lower() == "true"

    notifications = get_pending_notifications()

    print("Pending notifications:", len(notifications))

    for post in notifications:

        if not enabled:

            send_notification(post, dry_run=True)

            continue

        if not claim_notification(post["id"]):
            continue

        try:

            response = send_notification(
                post,
                dry_run=False
            )

            count = response.group_info.count

            if count.registered_success == 1:

                mark_accepted(
                    post["id"],
                    response.group_info.group_id
                )

            elif count.registered_failed == 1:

                mark_failed(
                    post["id"],
                    "SOLAPI rejected the message."
                )

            else:

                mark_failed(
                    post["id"],
                    "Unexpected API response.",
                    status="unknown"
                )

        except Exception as error:

            mark_failed(
                post["id"],
                type(error).__name__,
                status="unknown"
            )

            print("SMS request failed. Check SOLAPI history.")


def main():

    init_db()

    print("\nChecking DOOR...\n")

    assignments = scrape_assignments()

    notices, materials = scrape_posts()

    for assignment in assignments:

        assignment["type"] = "assignment"
        assignment["url"] = DOOR_URL

    all_posts = assignments + notices + materials

    new_posts = save_posts(all_posts)

    print("\n========== SUMMARY ==========\n")

    print("Assignments:", len(assignments))
    print("Notices:", len(notices))
    print("Lecture materials:", len(materials))
    print("Total stored posts:", count_posts())
    print("New posts:", len(new_posts))

    print("\n========== NOTIFICATIONS ==========\n")

    process_notifications()

    print("\nDOOR check completed.")


if __name__ == "__main__":
    main()