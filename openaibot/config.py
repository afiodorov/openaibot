import os

openai_token = os.getenv("OPENAIBOT_OPENAI_API_KEY", "")

telegram_token_en = os.getenv("OPENAIBOT_TELEGRAM_TOKEN_EN", "")
telegram_token_es = os.getenv("OPENAIBOT_TELEGRAM_TOKEN_ES", "")
telegram_token_ru = os.getenv("OPENAIBOT_TELEGRAM_TOKEN_RU", "")

telegram_secret = os.getenv("OPENAIBOT_TELEGRAM_SECRET", "")

user_whitelist = os.getenv("OPENAIBOT_USER_WHITELIST", "").split(",")
