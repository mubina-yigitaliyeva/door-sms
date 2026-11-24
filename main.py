from scraper import scrape_assignments, scrape_posts
from database import init_db, save_posts, count_posts
from config import DOOR_URL


def main():

    init_db()

    print("\nChecking DOOR...\n")

    assignments = scrape_assignments()
    notices, materials = scrape_posts()

    for assignment in assignments:

        assignment["type"] = "assignment"
        assignment["url"] = DOOR_URL

    all_posts = assignments + notices + materials

    print("\n========== SUMMARY ==========\n")

    print("Assignments:", len(assignments))
    print("Notices:", len(notices))
    print("Lecture materials:", len(materials))

    new_posts = save_posts(all_posts)

    print("\n========== DATABASE ==========\n")

    print("Total stored posts:", count_posts())
    print("New posts:", len(new_posts))

    if not new_posts:

        print("No new notifications.")

    else:

        for post in new_posts:

            print("\nNEW POST DETECTED!")
            print("Type:", post["type"])
            print("Title:", post["title"])
            print("-" * 50)


if __name__ == "__main__":
    main()