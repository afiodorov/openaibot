import logging
from typing import Any, Optional, Tuple

import requests

from ..config import telegram_token_en, telegram_token_es, telegram_token_ru

tokens = {"en": telegram_token_en, "es": telegram_token_es, "ru": telegram_token_ru}


def parse_received(
    logger: logging.Logger, msg: Optional[Any]
) -> Tuple[Optional[str], Optional[str]]:
    if not isinstance(msg, dict):
        return None, None

    try:
        from_ = msg["message"]["chat"]["id"]
        body = msg["message"]["text"]

        return from_, body
    except KeyError:
        return None, None


def send_text(logger: logging.Logger, to: str, body: str, lang: str = "en") -> None:
    if lang not in tokens:
        logger.error(f"no token for lang {lang}")
        return

    telegram_token = tokens[lang]
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    msg = {
        "chat_id": to,
        "text": body,
    }

    res = requests.post(url, json=msg)

    if not res.ok:
        logger.error(res.content)
