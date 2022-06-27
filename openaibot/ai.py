import os
import openai

from .config import openai_token
from textwrap import dedent

openai.api_key = openai_token


def get_response(logging, msg: str, history):
    historical_dialogue = "\n".join(
        f"Human: {i.request}\nAI: {i.response}" for i in history
    )

    prompt = dedent(
        f"""\
{historical_dialogue}
Human: {msg}
AI:
    """.rstrip()
    )

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        temperature=0.9,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"],
    )

    reply = response["choices"][0]["text"]

    return reply.strip()
