import httpx
from backend.app.settings import settings


def send_sync_tg_message(message: str):
    if message:
        tg_msg = {
            "chat_id": settings.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        api_url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
        with httpx.Client(timeout=180) as client:
            response = client.post(api_url, json=tg_msg)
            response.raise_for_status()
