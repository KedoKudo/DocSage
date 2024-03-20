"""Simple chatbot based on the OLLAMA+RAG."""
#!/usr/bin/env python
import os
import tempfile
import streamlit as st
import ollama
from docsage.model import LLM
from langchain_community.callbacks import StreamlitCallbackHandler

# Layout
# get list of models available
ollama_models = ollama.list()["models"]
st.sidebar.title("Control Panel")
model_selection = st.sidebar.selectbox(
    "Select the Model",
    options=[model["name"] for model in ollama_models],
)
selected_model = next(
    (model for model in ollama_models if model["name"] == model_selection), None
)
if selected_model:
    st.sidebar.write(f"Size/GB: {float(selected_model['size'])/(1024**3):.2f}")

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.85,
)
uploaded_file = st.sidebar.file_uploader(
    "Upload a file for RAG",
    type=["pdf", "txt"],
    accept_multiple_files=True,
)

# select pre-processed knowledge base
db_selection = st.sidebar.selectbox(
    "Select the knowledge base",
    options=[
        "None",
        # "Mantid",
        # "HyGNN",
        "iMars3D",
    ],
)

# Chatbot
st.title("DocSage")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        container = st.container()
        container.write(message["content"])

# Initialize the model
model = LLM(
    model_name=model_selection,
    temperature=temperature,
    knowledge_base=db_selection,
)

# Chatbot interface
if user_prompt := st.chat_input("Ask me anything", key="chat_input"):
    # display input prompt
    with st.chat_message("user"):
        st.write(user_prompt)

    # display response
    if uploaded_file:
        # ingest
        for file in uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                tf.write(file.getbuffer())
                file_path = tf.name

            with st.spinner(f"Ingesting {file.name}"):
                # determine the type of file
                if file.name.endswith(".pdf"):
                    model.update_vectordb(file_path, file_type="pdf")
                elif file.name.endswith(".txt"):
                    model.update_vectordb(file_path, file_type="txt")
                else:
                    st.error("Unsupported file type")
                    os.remove(file_path)
                    continue

            os.remove(file_path)
    #
    with st.chat_message("🦖"):
        callback = StreamlitCallbackHandler(
            st.container(), collapse_completed_thoughts=False
        )

        # Monkey patch to remove the default empty text in a container
        # org_on_llm_start = callback.on_llm_start

        # def new_on_llm_start(*args, **kwargs):
        #     org_on_llm_start(*args, **kwargs)
        #     callback._current_thought._container.write("")

        # callback.on_llm_start = new_on_llm_start

        model.set_callbacks(callback)
        response = model.qa.invoke(user_prompt)
        msg = response["result"] if isinstance(response, dict) else response

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.session_state.messages.append({"role": "🦖", "content": msg})
