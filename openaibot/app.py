import logging
from datetime import datetime, timezone

from flask import Flask, abort, request
from pythonjsonlogger import jsonlogger
from werkzeug.middleware.proxy_fix import ProxyFix

from .ai import get_response_new
from .chats import telegram
from .config import telegram_secret
from .lobby import Lobby
from .state import Interaction, state


def setup_log():
    class ISOJsonFormatter(jsonlogger.JsonFormatter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def formatTime(self, record, datefmt=None) -> str:
            dt = datetime.fromtimestamp(record.created, timezone.utc)
            return dt.isoformat() + "Z"

    logger = logging.getLogger()

    logHandler = logging.StreamHandler()
    formatter = ISOJsonFormatter(
        "%(asctime)s %(levelname)s %(message)s", json_ensure_ascii=False
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.level = logging.INFO


def create_app() -> Flask:
    setup_log()

    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)  # type: ignore

    lobby = Lobby(app.logger)

    @app.route("/twebhook<lang>", methods=["POST"])
    def webhook_telegram(lang: str) -> str:
        given_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if given_token != telegram_secret:
            abort(403)

        from_, body = telegram.parse_received(app.logger, request.json)
        if body == "/start":
            return ""

        if from_ is None or body is None:
            app.logger.info(f"invalid message: {request.json}")
            return ""

        user = f"telegram:{lang}:{from_}"
        lobby.clean_up()
        if not lobby.is_allowed(user):
            telegram.send_text(
                app.logger,
                from_,
                f"too many current users: {len(lobby.current_users)}",
                lang=lang,
            )
            return ""

        history = state[user]

        if body == "/clear":
            history.clear()
            return ""

        resp = get_response_new(app.logger, body, history, lang=lang)
        history.append(Interaction(request=body, response=resp))
        lobby.register(user)

        telegram.send_text(app.logger, from_, resp, lang=lang)

        return ""

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
