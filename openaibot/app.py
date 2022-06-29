import logging

from flask import Flask, abort, request
from werkzeug.middleware.proxy_fix import ProxyFix

from .ai import get_response, prompts
from .chats import telegram
from .config import telegram_secret
from .lobby import Lobby
from .state import Interaction, state


def create_app() -> Flask:
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)  # type: ignore

    logging.basicConfig(level=logging.INFO)

    lobby = Lobby(app.logger)

    @app.route("/twebhoo<lang>", methods=["POST"])
    def webhook_telegram(lang: str) -> str:
        if len(lang) > 0:
            lang = lang[1:]

        if lang not in prompts:
            lang = "en"

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
        resp = get_response(app.logger, body, history, lang=lang)
        history.append(Interaction(request=body, response=resp))
        lobby.register(user)

        telegram.send_text(app.logger, from_, resp, lang=lang)

        return ""

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
