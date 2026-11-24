import os
import time
from datetime import datetime

from dotenv import load_dotenv
from main import main

load_dotenv()

INTERVAL = max(
    15,
    int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))
) * 60


def monitor():

    print("DOOR-SMS monitoring started.")
    print(f"Checking every {INTERVAL // 60} minutes.")
    print("Press Ctrl+C to stop.")

    while True:

        print("\n" + "=" * 50)

        print(
            "Checking time:",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        try:

            main()

        except Exception as error:

            print("Monitoring error:", type(error).__name__)
            print("Check your connection and DOOR login session.")

            if type(error).__name__ == "TimeoutError":
                print("Monitoring stopped. Check DOOR manually.")
                return

        print(f"\nNext check in {INTERVAL // 60} minutes.")

        time.sleep(INTERVAL)


if __name__ == "__main__":

    try:

        monitor()

    except KeyboardInterrupt:

        print("\nDOOR-SMS monitoring stopped.")