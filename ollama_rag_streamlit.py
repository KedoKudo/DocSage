"""Simple chatbot based on the OLLAMA+RAG."""
#!/usr/bin/env python
import streamlit as st 
from langchain_community.llms import Ollama
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class LLM:

    def __init__(self, model_name: str="mistral", temperature: float=0.5):
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


def main():
    # Layout
    st.sidebar.title("Control Panel")
    model_selection = st.sidebar.selectbox(
        "Select the Model",
        options=["mistral", "llama2", "codellama"],
    )
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
    )
    uploaded_file = st.sidebar.file_uploader(
        "Upload a file for RAG",
        type=['pdf'],
    )

    model = LLM(
        model_name=model_selection,
        temperature=temperature,
    )

    # Chatbot
    st.title("Simple OLLAMA+RAG Chatbot")
    chat_container = st.empty()
    input_text = st.text_input("Your message:", key="chat_input")
    if st.button("Send"):
        chat_container.write_stream(model.llm.stream(input_text))


if __name__ == "__main__":
    main()
