import time
import config
from helper import *

def main():
    last_first_page_data = None

    # --- Initial scrape ---
    all_press_releases = scrape_all_pages()
    print_press_releases_json(all_press_releases)
    asyncio.run(send_to_websocket(all_press_releases))

    # Save first page data to compare later
    first_page_content = fetch_page_content(1)
    last_first_page_data = extract_press_releases(first_page_content)

    # --- Periodic check for new press releases ---
    while True:
        time.sleep(config.CHECK_INTERVAL)
        try:

            new_first_page_content = fetch_page_content(1)
            new_first_page_data = extract_press_releases(new_first_page_content)
            if not new_first_page_data:
                raise Exception("Check failed: extracted data is empty")

            if new_first_page_data != last_first_page_data:
                print("\n=== New press releases detected! Refreshing all pages... ===\n")
                all_press_releases = scrape_all_pages()
                print_press_releases_json(all_press_releases)
                asyncio.run(send_to_websocket(all_press_releases))

                # Pushover notification for latest article
                latest_article = new_first_page_data[0]
                send_pushover_notification(
                    "New Ripple Press Release",
                    f"{latest_article['title']} ({latest_article['date']})",
                    priority=1
                )

                last_first_page_data = new_first_page_data
            else:
                print("No new updates, checking again in 3 seconds...")

        except Exception as e:
                # ---- CHECK FAILED → SEND PUSHOVER ----
                send_pushover_notification(
                    "🚨 Ripple Press Release Check Failed",
                    str(e), priority=1
                )

if __name__ == "__main__":
    main()
