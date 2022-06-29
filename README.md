# OpenAI Telegram Chatbot

Made for fun

# Installing & running.

1. [Install poetry][poetry]
2. Run `poetry install`
3. Run `waitress-serve --host=127.0.0.1 --port=5000 openaibot:app`
4. Follow [nginx guide][nginx].
5. Use [Bot father][father] and [setwebhook][setwebhook] call.

[poetry]: https://python-poetry.org/docs/
[nginx]: https://flask.palletsprojects.com/en/2.1.x/deploying/nginx/
[father]: https://t.me/BotFather
[setwebhook]: https://core.telegram.org/bots/api#setwebhook
