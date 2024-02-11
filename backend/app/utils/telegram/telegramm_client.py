import os

import httpx

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


async def send_tg_message(message: str):
    if message:
        tg_msg = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        async with httpx.AsyncClient(timeout=180) as client:
            await client.post(api_url, json=tg_msg)
