import httpx

from app.settings import settings


async def send_tg_message(message: str):
    if message:
        tg_msg = {"chat_id": settings.chat_id, "text": message, "parse_mode": "Markdown"}
        api_url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
        async with httpx.AsyncClient(timeout=180) as client:
            await client.post(api_url, json=tg_msg)
