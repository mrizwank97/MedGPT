import os
import weave
from groq import Groq


def get_client(
    chat_model: str,
    temperature: int,
    max_tokens: int,
    top_p: int,
    stream: bool,
    chat_stop: str,
    json_format: bool = True,
):
    print(f"Using {chat_model} for evaluation")
    if any(model in chat_model for model in ("llama3-70b-8192", "mixtral-8x7b-32768")):
        return GroqLLMClient(
            chat_model=chat_model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=stream,
            chat_stop=chat_stop,
            json_format=json_format,
        )
    return None


class BaseLLMClient:
    def send_prompt(self, prompt):
        raise NotImplementedError("method send_message must be implemented!!")


class GroqLLMClient(BaseLLMClient):
    def __init__(
        self,
        chat_model,
        temperature,
        max_tokens,
        top_p,
        stream=False,
        chat_stop=None,
        json_format=True,
    ):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.groq_model = Groq(api_key=self.api_key)
        self.chat_model = chat_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stream = stream
        self.stop = chat_stop
        self.json_format = json_format

    @weave.op()
    def send_message(self, prompt):
        common_args = {
            "model": self.chat_model,
            "messages": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": bool(self.stream),
            "stop": self.stop,
        }

        if self.json_format:
            common_args["response_format"] = {"type": "json_object"}

        output = self.groq_model.chat.completions.create(**common_args)
        return output
