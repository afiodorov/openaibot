import requests

from typing import Dict
from ..config import telegram_token


def parse_received(logger, msg: Dict):
    try:
        from_ = msg["message"]["chat"]["id"]
        body = msg["message"]["text"]

        return from_, body
    except KeyError:
        return None, None


def send_text(logger, to: str, body: str):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    msg = {
        "chat_id": to,
        "text": body,
    }

    res = requests.post(url, json=msg)

    if not res.ok:
        logger.error(res.content)
