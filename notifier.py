import os

from dotenv import load_dotenv
from solapi import SolapiMessageService
from solapi.model import RequestMessage
from config import DOOR_URL

load_dotenv()


def format_message(post):

    labels = {
        "assignment": "New Assignment",
        "notice": "New Notice",
        "lecture_material": "New Lecture Material"
    }

    lines = [f"[DOOR-SMS] {labels[post['type']]}"]

    if post.get("course"):
        lines.append(f"Course: {post['course']}")

    lines.append(f"Title: {post['title']}")

    if post.get("deadline"):
        lines.append(f"Due: {post['deadline']}")

    lines.append(DOOR_URL)

    return "\n".join(lines)


def send_notification(post, dry_run=True):

    text = format_message(post)

    print("\n========== NOTIFICATION ==========")
    print(text)

    if dry_run:
        print("Preview mode: No SMS sent.")
        return None

    service = SolapiMessageService(
        api_key=os.environ["SOLAPI_API_KEY"],
        api_secret=os.environ["SOLAPI_API_SECRET"]
    )

    message = RequestMessage(
        from_=os.environ["SMS_SENDER"],
        to=os.environ["SMS_RECEIVER"],
        text=text
    )

    response = service.send(message)

    print("Group ID:", response.group_info.group_id)
    print("Accepted:", response.group_info.count.registered_success)
    print("Failed:", response.group_info.count.registered_failed)

    return response