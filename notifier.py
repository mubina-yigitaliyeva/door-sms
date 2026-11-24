from config import DOOR_URL


def format_message(post):

    labels = {
        "assignment": "New Assignment",
        "notice": "New Notice",
        "lecture_material": "New Lecture Material"
    }

    label = labels[post["type"]]

    lines = [f"[DOOR-SMS] {label}"]

    if post.get("course"):
        lines.append(f"Course: {post['course']}")

    lines.append(f"Title: {post['title']}")

    if post.get("deadline"):
        lines.append(f"Due: {post['deadline']}")

    lines.append(DOOR_URL)

    return "\n".join(lines)


def send_notification(post):

    message = format_message(post)

    print("\n========== SMS PREVIEW ==========")
    print(message)
    print("=================================")

    return message