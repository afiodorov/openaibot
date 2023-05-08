import logging
from textwrap import dedent
from typing import Iterable

import openai
import requests
from requests.auth import HTTPBasicAuth

from .config import gpt_pass, gpt_url, gpt_user, openai_token
from .state import Interaction

openai.api_key = openai_token

prompts = {
    "en": {
        "start": "Following conversation is between a human and AI Assistant.",
        "human": "Human",
        "ai": "AI Assistant",
    },
    "es": {
        "start": (
            "La siguiente es una conversación con un asistente de AI. El asistente es útil,"
            " creativo, inteligente y muy amigable."
        ),
        "human": "Humano",
        "ai": "AI",
    },
    "ru": {
        "start": (
            "Далее следует разговор с AI-помощником. Помощник услужливый, творческий, умный и очень"
            " дружелюбный."
        ),
        "human": "Человек",
        "ai": "AI",
    },
}


def get_response(
    logging: logging.Logger, msg: str, history: Iterable[Interaction], lang: str = "en"
) -> str:
    start = prompts[lang]["start"]
    human = prompts[lang]["human"]
    ai = prompts[lang]["ai"]

    historical_dialogue = "\n".join(
        f"{human}: {i.request}\n{ai}: {i.response}" for i in history
    )

    prompt = dedent(
        f"""\
{start}
{historical_dialogue}
{human}: {msg}
{ai}:
    """.strip()
    )

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.9,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[f" {human}:", f" {ai}:"],
    )

    reply = str(response["choices"][0]["text"])
    reply = reply.split(f"\n{human}:")[0]

    return reply.strip()


def get_response_new(
    logging: logging.Logger, msg: str, history: Iterable[Interaction], lang: str = "en"
) -> str:
    start = prompts[lang]["start"]
    human = prompts[lang]["human"]
    ai = prompts[lang]["ai"]

    historical_dialogue = "\n".join(
        f"{human}: {i.request}\n{ai}: {i.response}" for i in history
    )

    prompt = dedent(
        f"""\
{start}
{historical_dialogue}
{human}: {msg}
{ai}:
    """.strip()
    )

    headers = {"Content-Type": "application/json"}

    resp = requests.post(
        gpt_url,
        auth=HTTPBasicAuth(gpt_user, gpt_pass),
        json={"prompt": prompt},
        headers=headers,
    )

    if not resp.ok:
        logging.error(resp.text)
        return ""

    reply = resp.json()["completion"]
    reply = reply.split(f"\n{human}:")[0]

    return reply.strip()
