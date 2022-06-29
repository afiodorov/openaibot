import logging
from datetime import datetime, timezone
from typing import Dict

from .config import user_whitelist

max_num_users = 5


class Lobby:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.current_users: Dict[str, datetime] = {}

    def clean_up(self) -> None:
        now = datetime.now(timezone.utc)
        self.current_users = {
            k: v for k, v in self.current_users.items() if (now - v).seconds < 3600
        }

    def is_allowed(self, user: str) -> bool:
        if user in user_whitelist:
            return True

        if user in self.current_users:
            return True

        if len(self.current_users) <= max_num_users:
            return True

        return False

    def register(self, user: str) -> None:
        if user in user_whitelist:
            return

        self.current_users[user] = datetime.now(timezone.utc)
        self.logger.info(f"current number of active users: {len(self.current_users)}")
