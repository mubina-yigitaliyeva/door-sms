from playwright.sync_api import sync_playwright
from config import DOOR_URL, AUTH_FILE
from scraper import get_courses
from urllib.parse import urljoin


def inspect_classroom():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            storage_state=str(AUTH_FILE)
        )

        page = context.new_page()

        page.goto(DOOR_URL)

        courses = get_courses(page)

        course = next(
            c for c in courses
            if "웹프로그래밍" in c["title"]
        )

        course_id = course["id"]

        sections = {
            "공지사항": f"/CRoom/Notice/{course_id}",
            "강의자료": f"/CRoom/CourseReference/{course_id}"
        }

        for name, link in sections.items():

            page.goto(urljoin(DOOR_URL, link))

            heading = page.get_by_text(
                name, exact=True
            ).last

            heading.wait_for(timeout=15000)

            section = heading.locator("../..")

            print(f"\n----- {name} -----\n")

            print(section.inner_text())

            print("\n----- HTML STRUCTURE -----\n")

            print(
                section.evaluate(
                    "(element) => element.outerHTML"
                )
            )

        browser.close()


if __name__ == "__main__":
    inspect_classroom()