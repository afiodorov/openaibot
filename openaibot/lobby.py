import logging
from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from typing import DefaultDict, Dict, Iterable, Protocol

from .ai import get_response_local, get_response_openai
from .config import user_whitelist
from .state import Interaction

max_num_users = 15


class Model(Enum):
    GPT3 = 1
    LOCAL = 2


class Inference(Protocol):
    def __call__(
        self,
        logging: logging.Logger,
        msg: str,
        history: Iterable[Interaction],
        lang: str = "en",
    ) -> str:
        pass


class Lobby:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.current_users: Dict[str, datetime] = {}
        self.inference: DefaultDict[str, Inference] = defaultdict(
            lambda: get_response_local
        )

        for user in user_whitelist[1:]:
            self.inference[user] = get_response_openai

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

    def switch_user(self, user: str, model: Model) -> bool:
        if user not in user_whitelist:
            return False

        if model == Model.GPT3:
            self.inference[user] = get_response_openai
            return True

        if model == Model.LOCAL:
            self.inference[user] = get_response_local
            return True

        return False
