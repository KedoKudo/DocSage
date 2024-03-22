"""Simple chatbot based on the OLLAMA+RAG."""
#!/usr/bin/env python
import os
import json
import tempfile
import streamlit as st
import ollama
from docsage.model import LLM
from langchain_community.callbacks import StreamlitCallbackHandler

# ------------------------------
# --------- Control Panel ------
# ------------------------------
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
    value=0.5,
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
        "Mantid",
        "iMars3D",
    ],
    index=None,
)

# toggle to show/hide source documents for RAG
show_source_documents = st.sidebar.checkbox("Show source documents", value=False)

# Initialize the model
model = LLM(
    model_name=model_selection,
    temperature=temperature,
    knowledge_base=db_selection,
    return_source_documents=show_source_documents,
)

# add a reset context button
if st.sidebar.button("Reset Context"):
    model.reset_context()

# ------------------------------
# --------- Chatbot UI ---------
# ------------------------------
st.image("resources/icon.png", width=50)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        container = st.container()
        container.write(message["content"])

# add a button to clean the chat history only if there is chat history
if st.session_state.messages:
    cols = st.columns(6, gap="large")

    with cols[0]:
        if st.button("🗑️"):
            st.session_state.messages = []
            st.experimental_rerun()

    with cols[-1]:
        # button to save the chat history to file to save to disk
        st.download_button(
            "💾",
            data=json.dumps(st.session_state.messages, indent=2),
            file_name="chat_history.json",
            mime="application/json",
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
    with st.chat_message("🧙🏼‍♂️"):
        callback = StreamlitCallbackHandler(
            st.container(), collapse_completed_thoughts=False
        )

        model.set_callbacks(callback)
        response = model.qa.invoke(user_prompt)
        msg = response["result"] if isinstance(response, dict) else response

        # if show source documents, display them
        if show_source_documents:
            src_docs = response.get("source_documents", None)
            st.markdown("source docs", help=str(src_docs))

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.session_state.messages.append({"role": "🧙🏼‍♂️", "content": msg})
