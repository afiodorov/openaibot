import os

openai_token = os.getenv('OPENAIBOT_OPENAI_API_KEY', "")

telegram_token = os.getenv('OPENAIBOT_TELEGRAM_TOKEN', "")
telegram_secret = os.getenv('OPENAIBOT_TELEGRAM_SECRET', "")

user_whitelist = os.getenv('OPENAIBOT_USER_WHITELIST', "").split(",")
