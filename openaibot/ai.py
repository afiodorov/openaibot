import logging
import re
from textwrap import dedent
from typing import Iterable

import openai
import requests
from requests.auth import HTTPBasicAuth

from .config import gpt_cheap_url, gpt_pass, gpt_user, openai_token
from .state import Interaction

openai.api_key = openai_token

prompts = {
    "en": {
        "start": (
            "Let's follow this conversation between a human and AI Assistant."
            " AI Assistant works out every question in a step by step way to be sure it gives"
            " the right answer"
        ),
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


def remove_last_unmatched_bracket(text: str) -> str:
    counter = 0

    for char in text:
        if char == "{":
            counter += 1
        elif char == "}":
            counter -= 1

    if counter < 0:
        return text.rstrip("}")

    return text


def clean_up(resp: str) -> str:
    pattern = r"\n\s*(?!(?:Example:))([A-Z][a-z]+:)"
    split_text = re.split(pattern, resp)
    text_before_match = split_text[0]

    return remove_last_unmatched_bracket(text_before_match.strip())


def get_response_openai(
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
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=2048,
        top_p=1,
        best_of=3,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[f" {human}:", f" {ai}:"],
    )

    reply = str(response["choices"][0]["text"])

    return clean_up(reply)


def get_response_local(
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

    resp = requests.post(
        gpt_cheap_url,
        auth=HTTPBasicAuth(gpt_user, gpt_pass),
        json={"prompt": prompt},
    )

    if not resp.ok:
        logging.error(resp.text)
        return ""

    return clean_up(resp.json().get("completion", ""))
