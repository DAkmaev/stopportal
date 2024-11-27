import json

import httpx
from backend.app.settings import settings


def send_update_db_request(decisions_json: json, user_id: int):
    if decisions_json:
        api_url = f"{settings.internal_api_url}ta/{user_id}"
        with httpx.Client(timeout=180) as client:
            response = client.post(api_url, json=decisions_json)
            response.raise_for_status()
