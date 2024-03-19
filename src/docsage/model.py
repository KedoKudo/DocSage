"""Main LLM interface class."""
#!/usr/bin/env python
from langchain_community.llms import Ollama
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory


class LLM:
    def __init__(
        self, model_name: str = "mistral", temperature: float = 0.5, callbacks=None
    ):
        self.model_name = model_name
        self.callback = (
            StreamingStdOutCallbackHandler() if callbacks is None else callbacks
        )
        self.llm = Ollama(
            model=model_name,
            temperature=temperature,
            callbacks=[self.callback],
        )
        self.msg_history = []
        self.embeddings = OllamaEmbeddings()
        # start a default chroma vector database for RAG model
        # self.vector_db = Chroma(
        #     # persist_directory="./chroma_db",
        #     embedding_function=self.embeddings,
        # )
        self.vector_db = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=64,
        )
        #
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

    @property
    def qa(self):
        if self.vector_db:
            return RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_db.as_retriever(),
                memory=self.memory,
            )
        else:
            return self.llm

    def set_model(self, model_name: str):
        self.model_name = model_name
        self.llm = Ollama(
            model=model_name,
            callbacks=[self.callback],
        )

    def set_callbacks(self, callbacks):
        self.callback = callbacks
        self.llm.callbacks = [self.callback]

    def set_temperature(self, temperature: float):
        self.llm.temperature = temperature

    def update_vectordb(self, new_file: str):
        """Load the new file into the vector database.

        Parameters
        ----------
        new_file : str
            The path to the new file.
        """
        # decide which loader to use
        if new_file.endswith(".pdf"):
            loader = PyPDFLoader(new_file)
        else:
            loader = TextLoader(new_file)
        pages = loader.load_and_split()
        all_splits = self.text_splitter.split_documents(pages)
        if self.vector_db:
            self.vector_db.add_documents(all_splits)
        else:
            self.vector_db = Chroma.from_documents(
                all_splits,
                embedding=self.embeddings,
            )
