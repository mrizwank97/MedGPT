import requests
from typing import Union

from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/")
def home():
    return {"hello": "World"}


@app.get("/ask")
def ask(
    model: str,
    prompt: str,
    seed: Union[int, None] = None,
    max_tokens: Union[int, None] = None,
):
    options = {}
    if seed is not None:
        options["seed"] = seed

    if max_tokens is not None:
        options["num_predict"] = max_tokens

    prefix_text = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n"
    instruction = "Please answer with one of the option in the bracket. Write reasoning in between <analysis></analysis>. Write answer in between <answer></answer>. Here are the inputs: "
    text = f"""<start_of_turn>user {prefix_text}{instruction}{prompt} <end_of_turn>\n<start_of_turn>model"""

    res = requests.post(
        "http://ollama:11434/api/generate",
        json={
            "prompt": text,
            "stream": False,
            "model": model,
            "options": options,
        },
    )

    return Response(content=res.text, media_type="application/json")
