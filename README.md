markdown
# Ripple Scraping WebSocket Notification Project

## Description

This project monitors Ripple Press releases. It automatically scrapes the latest press release data and sends it to a WebSocket server. Every 2–3 seconds, it checks again to see whether any new press releases have been published.

If a new press release is detected, it is scraped and sent through the WebSocket, and a Pushover notification is also sent. If any error occurs while checking or scraping, a priority-1 Pushover notification is sent to alert you.

In summary, the script:

- Scrapes Ripple Press releases
- Sends the data to a WebSocket server
- Re-checks every 2–3 seconds for new releases
- Sends Pushover notifications for:
  - any new press release
  - any issues or errors during checking or scraping

The project is built in Python and is easy to configure and run.

---

## Installation

### Step 1 — (Optional but recommended) Create virtual environment

**Windows**
```git
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```git
python3 -m venv venv
source venv/bin/activate
````

### Step 2 — Install required dependencies
```git
pip install -r requirements.txt
```

### Configuration
Edit your configuration file (for example config.py) and add:

```python
CHECK_INTERVAL = 3
WEBSOCKET_URL = "ws://localhost:5000"  # Replace with your EC2 WebSocket URL
PUSHOVER_USER_KEY = "your_user_key"   # Replace with your Pushover user key
PUSHOVER_APP_TOKEN = "your_app_token" # Replace with your Pushover app token
```

### Run
Run the main script:
```git
python main.py
```
