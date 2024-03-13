"""Panel based simple chatbot based on the OLLAMA+RAG."""
import panel as pn
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


# control panel
model_selection = pn.widgets.Select(
    name="Select the Model",
    options=["mistral", "llama2", "codellama"],
)
temperature = pn.widgets.FloatSlider(
    name="Temperature",
    start=0.0,
    end=1.0,
    value=0.5,
)
uploaded_file = pn.widgets.FileInput(
    name="Upload a file for RAG",
    accept=".pdf",
)
# group control panel
control_panel = pn.Column(
    model_selection,
    temperature,
    uploaded_file,
)

# chatbot
chat_container = pn.pane.Markdown("", width=800)
input_text = pn.widgets.TextInput(
    name="Your message:",
)
send_button = pn.widgets.Button(
    name="Send",
)
# group chatbot
chatbot = pn.Column(
    chat_container,
    input_text,
    send_button,
)

# model
model = LLM(
    model_name=model_selection.value,
    temperature=temperature.value,
)

# layout
def on_click(event):
    chat_container.object = f"User: {input_text.value}\n"
    msg = ""
    for chunk in model.llm.stream(input_text.value):
        msg += chunk
        chat_container.object = f"Bot: {msg}"
send_button.on_click(on_click)

model_selection.param.watch(model.set_model, "value")
temperature.param.watch(model.set_temperature, "value")


app = pn.Row(
    control_panel,
    chatbot,
)

# serve with template
pn.template.FastListTemplate(
    title="Simple OLLAMA+RAG Chatbot",
    main=[app],
    header_background="#00A170",
    theme_toggle=True,
).servable()
