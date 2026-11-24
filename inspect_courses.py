from playwright.sync_api import sync_playwright
from config import DOOR_URL, AUTH_FILE


def inspect_courses():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            storage_state=str(AUTH_FILE)
        )

        page = context.new_page()

        page.goto(DOOR_URL)

        heading = page.get_by_text(
            "나의 강의", exact=True
        ).first

        heading.wait_for(timeout=15000)

        section = heading.locator("../..")

        print(section.inner_text())

        print("\n----- HTML STRUCTURE -----\n")

        print(
            section.evaluate(
                "(element) => element.outerHTML"
            )
        )

        browser.close()


if __name__ == "__main__":
    inspect_courses()