import requests
import brotli
import re
import json
import asyncio
import websockets
from bs4 import BeautifulSoup
import config
# -----------------------------
# CONFIGURATION
# -----------------------------
BASE_URL = "https://ripple.com/press-releases/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

WEBSOCKET_URL = config.WEBSOCKET_URL
PUSHOVER_USER_KEY = config.PUSHOVER_USER_KEY
PUSHOVER_APP_TOKEN = config.PUSHOVER_APP_TOKEN

# -----------------------------
# SCRAPING FUNCTIONS
# -----------------------------
def get_total_pages():
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    pagination_div = soup.find("div", class_="flex items-center justify-center")

    if pagination_div:
        links = pagination_div.find_all("a")
        page_numbers = []
        for link in links:
            if link.div:
                try:
                    page_numbers.append(int(link.div.get_text(strip=True)))
                except ValueError:
                    continue
        if page_numbers:
            return max(page_numbers)
    return 1


def fetch_page_content(page_number):
    url = f"{BASE_URL}page/{page_number}/?_rsc=yk8p9"
    headers = HEADERS.copy()
    headers.update({
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": f"{BASE_URL}page/{page_number}/",
        "rsc": "1"
    })

    response = requests.get(url, headers=headers)
    encoding = response.headers.get("Content-Encoding", "").lower()

    if encoding == "br":
        try:
            content = brotli.decompress(response.content).decode("utf-8")
        except (brotli.error, AttributeError):
            content = response.content.decode("utf-8", errors="ignore")
    else:
        content = response.text
    return content


def extract_press_releases(content):
    press_releases = []
    pattern = r'"line-clamp-3 text-gray-2\.5 heading2 mb-auto".*?"children":"([^"]+)".*?"text-gray-30 caption1".*?"children":"([^"]+)"'
    matches = re.findall(pattern, content, re.DOTALL)
    for title, date in matches:
        press_releases.append({"title": title.replace('\\"', '"'), "date": date})
    return press_releases


def scrape_all_pages():
    total_pages = get_total_pages()
    all_press_releases = []

    for page in range(1, total_pages + 1):
        content = fetch_page_content(page)
        all_press_releases.extend(extract_press_releases(content))

    return all_press_releases


def print_press_releases_json(press_releases):
    print(json.dumps(press_releases, indent=4, ensure_ascii=False))

# -----------------------------
# WEBSOCKET AND PUSHOVER
# -----------------------------
async def send_to_websocket(data):
    try:
        async with websockets.connect(WEBSOCKET_URL) as ws:
            await ws.send(json.dumps(data))
            print("✅ Data sent successfully to WebSocket")
    except Exception as e:
        print(f"WebSocket send failed: {e}")


def send_pushover_notification(title, message, priority=1):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_APP_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message,
        "priority": priority
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print("Pushover send failed:", response.text)
    except Exception as e:
        print(f"Pushover send failed: {e}")
