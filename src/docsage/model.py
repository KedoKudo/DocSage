"""Main LLM interface class."""
#!/usr/bin/env python
from langchain_community.llms import Ollama
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class LLM:
    def __init__(self, model_name: str = "mistral", temperature: float = 0.5):
        self.model_name = model_name
        self.llm = Ollama(
            model=model_name,
            temperature=temperature,
            callbacks=[StreamingStdOutCallbackHandler()],
        )
        self.msg_history = []

    def set_model(self, model_name: str):
        self.model_name = model_name
        self.llm = Ollama(
            model=model_name,
            callbacks=[StreamingStdOutCallbackHandler()],
        )

    def set_temperature(self, temperature: float):
        self.llm.temperature = temperature

    def update_vectordb(self, new_file: str):
        pass
