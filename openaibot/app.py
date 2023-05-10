import logging
from datetime import datetime, timezone
from http import HTTPStatus

from flask import Flask, abort, request
from pythonjsonlogger import jsonlogger
from werkzeug.exceptions import NotFound
from werkzeug.middleware.proxy_fix import ProxyFix

from .chats import telegram
from .config import telegram_secret, user_whitelist
from .lobby import Lobby, Model
from .state import Interaction, state
from .worker import Worker


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


help_msg = """APP: Welcome! Commands:
/clear - Make the bot forget forget history.
/gpt - Switch to OpenAI GPT3.5 model (whitelisted only).
/local - Switch to local model.
/help - Show this messasge.
""".strip()


def create_app() -> Flask:
    setup_log()

    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)  # type: ignore

    lobby = Lobby(app.logger)
    worker = Worker()

    worker.run()

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, NotFound):
            return "Not Found", HTTPStatus.NOT_FOUND

        app.logger.exception("Exception occurred")
        return "uncaught exception", HTTPStatus.INTERNAL_SERVER_ERROR

    @app.route("/twebhook<lang>", methods=["POST"])
    def webhook_telegram(lang: str) -> str:
        given_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if given_token != telegram_secret:
            abort(HTTPStatus.FORBIDDEN)

        from_, body = telegram.parse_received(app.logger, request.json)

        if from_ is None or body is None:
            app.logger.info(f"invalid message: {request.json}")
            return ""

        if body == "/start" or body == "/help":
            telegram.send_text(app.logger, from_, help_msg, lang=lang)
            return ""

        user = f"telegram:{lang}:{from_}"

        history = state[user]

        if body == "/clear":
            history.clear()
            telegram.send_text(app.logger, from_, "APP: History cleared", lang=lang)
            return ""

        if body == "/gpt":
            if lobby.switch_user(user, Model.GPT3):
                telegram.send_text(
                    app.logger, from_, "APP: Switched to GPT3", lang=lang
                )
            return ""

        if body == "/local":
            if lobby.switch_user(user, Model.LOCAL):
                telegram.send_text(
                    app.logger, from_, "APP: Switched to LOCAL", lang=lang
                )
            return ""

        if body == "/cheap":
            if lobby.switch_user(user, Model.CHEAP):
                telegram.send_text(
                    app.logger, from_, "APP: Switched to CHEAP", lang=lang
                )
            return ""

        lobby.clean_up()
        if not lobby.is_allowed(user):
            telegram.send_text(
                app.logger,
                from_,
                f"APP: Too many current users: {len(lobby.current_users)}",
                lang=lang,
            )
            return ""

        def send_reply():
            resp = lobby.inference[user](app.logger, body, history, lang=lang)
            history.append(Interaction(request=body, response=resp))
            lobby.register(user)
            telegram.send_text(app.logger, from_, resp, lang=lang)

        worker.push(1 if user not in user_whitelist else 10, send_reply)

        return ""

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
