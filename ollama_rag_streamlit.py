"""Simple chatbot based on the OLLAMA+RAG."""
#!/usr/bin/env python
import streamlit as st
from docsage.model import LLM

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
    type=["pdf"],
)

model = LLM(
    model_name=model_selection,
    temperature=temperature,
)

# Chatbot
st.title("Simple OLLAMA+RAG Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("Ask me anything", key="chat_input")

if user_prompt:
    # display input prompt
    with st.chat_message("user"):
        st.write(user_prompt)

    # display response
    with st.spinner("Thinking..."):
        msg = st.write_stream(model.llm.stream(user_prompt))
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.session_state.messages.append({"role": "bot", "content": msg})
