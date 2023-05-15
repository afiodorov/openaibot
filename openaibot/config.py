import os

from dotenv import load_dotenv

load_dotenv()

openai_token = os.getenv("OPENAIBOT_OPENAI_API_KEY", "")

telegram_token_en = os.getenv("OPENAIBOT_TELEGRAM_TOKEN_EN", "")
telegram_token_es = os.getenv("OPENAIBOT_TELEGRAM_TOKEN_ES", "")
telegram_token_ru = os.getenv("OPENAIBOT_TELEGRAM_TOKEN_RU", "")

telegram_secret = os.getenv("OPENAIBOT_TELEGRAM_SECRET", "")

user_whitelist = os.getenv("OPENAIBOT_USER_WHITELIST", "").split(",")

gpt_user = os.getenv("OPENAIBOT_GPT_USER", "")
gpt_pass = os.getenv("OPENAIBOT_GPT_PASS", "")
gpt_url = os.getenv("OPENAIBOT_GPT_URL", "")
gpt4_url = os.getenv("OPENAIBOT_GPT4_URL", "")
