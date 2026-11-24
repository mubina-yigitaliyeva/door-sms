from playwright.sync_api import sync_playwright
from config import DOOR_URL, AUTH_FILE
from urllib.parse import urljoin
import re
import time
from urllib.parse import urljoin

import hashlib

def get_assignments(page):

    page.locator(".list_wrap.todo").wait_for()

    items = page.locator(".todo_items").all()

    assignments = []

    for item in items:

        category = item.locator(
            ".cnt_tit > span:first-child"
        ).inner_text().strip()

        title = item.locator(
            ".cnt_tit .tit"
        ).inner_text().strip()

        deadline = item.locator(
            ".cnt_date span"
        ).inner_text().strip().lstrip("~")

        link = item.locator("a").get_attribute("onclick")

        unique_text = f"{category}|{title}|{link}"

        assignment_id = hashlib.sha256(
            unique_text.encode()
        ).hexdigest()

        assignment = {
            "id": assignment_id,
            "category": category,
            "title": title,
            "deadline": deadline
        }

        assignments.append(assignment)

    return assignments


def scrape_assignments():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            storage_state=str(AUTH_FILE)
        )

        page = context.new_page()

        page.goto(DOOR_URL)

        assignments = get_assignments(page)

        browser.close()

        return assignments

def get_courses(page):

    page.locator(".list_wrap.myLct").wait_for()

    items = page.locator(".myLct_list .lct_items").all()

    courses = []

    for item in items:

        category = item.locator(
            ".cnt_badge span"
        ).inner_text().strip()

        if category != "정규":
            continue

        title = item.locator(
            ".cnt_tit"
        ).inner_text().strip()

        link = item.locator("a").get_attribute("href")

        course_id = link.split("/")[-1]

        course = {
            "id": course_id,
            "title": title,
            "url": urljoin(DOOR_URL, link),
            "category": category
        }

        courses.append(course)

    return courses


def scrape_courses():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            storage_state=str(AUTH_FILE)
        )

        page = context.new_page()

        page.goto(DOOR_URL)

        courses = get_courses(page)

        browser.close()

        return courses

def get_posts(page, course, post_type):

    sections = {
        "notice": "Notice",
        "lecture_material": "CourseReference"
    }

    section = sections[post_type]

    url = urljoin(
        DOOR_URL,
        f"/CRoom/{section}/{course['id']}"
    )

    page.goto(url)

    posts = []
    visited_pages = set()

    while True:

        page.locator(".lctNotice .boardList").wait_for()

        items = page.locator(".boardList .boardItem").all()

        current_page = page.locator(
            ".paging input[name='pagenum']"
        ).get_attribute("value")

        if current_page in visited_pages:
            raise RuntimeError("Pagination did not advance.")

        visited_pages.add(current_page)

        print(f"  {post_type}: Page {current_page}")

        for item in items:

            title = item.locator(
                ".subject"
            ).inner_text().strip()

            date = item.locator(
                ".info_date"
            ).inner_text().strip()

            writer = item.locator(
                ".info_writer"
            ).inner_text().strip()

            onclick = item.locator(
                "a[onclick*='movedetail']"
            ).get_attribute("onclick")

            match = re.search(
                r"movedetail\((\d+)\)",
                onclick or ""
            )

            if not match:
                raise ValueError("Post ID not found.")

            post_id = match.group(1)

            posts.append({
                "id": f"{course['id']}_{post_type}_{post_id}",
                "post_id": post_id,
                "course_id": course["id"],
                "course": course["title"],
                "type": post_type,
                "title": title,
                "date": date,
                "writer": writer,
                "url": url
            })

        next_button = page.locator(".paging a.next")

        if next_button.count() == 0:
            break

        onclick = next_button.get_attribute("onclick")

        match = re.search(
            r"gopage\('mform','pagenum',\s*(\d+)",
            onclick or ""
        )

        if not match:
            break

        next_page = match.group(1)

        if int(next_page) <= int(current_page):
            break

        next_link = page.locator(
            ".paging ul li a"
        ).get_by_text(str(int(current_page) + 1), exact=True)

        time.sleep(2)

        if next_link.count() > 0:
            next_link.first.click()
        else:
            next_button.click()

        page.wait_for_function(
            """oldPage => {
                const input = document.querySelector(
                    '.paging input[name="pagenum"]'
                );
                return input && input.value !== oldPage;
            }""",
            arg=current_page,
            timeout=15000
        )

    return posts

def scrape_posts():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            storage_state=str(AUTH_FILE)
        )

        page = context.new_page()

        page.goto(DOOR_URL)

        courses = get_courses(page)

        notices = []
        materials = []

        try:

            for course in courses:

                print(f"Checking: {course['title']}")

                notices.extend(
                    get_posts(page, course, "notice")
                )

                time.sleep(2)

                materials.extend(
                    get_posts(page, course, "lecture_material")
                )

                time.sleep(2)

            return notices, materials

        finally:

            browser.close()