from playwright.sync_api import sync_playwright
from config import DOOR_URL, AUTH_FILE


def login():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        context = browser.new_context()
        page = context.new_page()

        page.goto(DOOR_URL)

        print("Please log in to DOOR manually.")

        input("Press Enter after successful login: ")

        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

        context.storage_state(path=str(AUTH_FILE))

        AUTH_FILE.chmod(0o600)

        print("Authentication session saved successfully.")

        browser.close()


if __name__ == "__main__":
    login()