from notifier import send_notification


assignment = {
    "type": "assignment",
    "course": "Object-Oriented Programming II",
    "title": "Final Project",
    "deadline": "2026-12-02"
}

notice = {
    "type": "notice",
    "course": "Linear Algebra",
    "title": "Final Exam Notice"
}

material = {
    "type": "lecture_material",
    "course": "Web Programming II",
    "title": "File Uploads and Management"
}


send_notification(assignment)
send_notification(notice)
send_notification(material)