"""Main LLM interface class."""
#!/usr/bin/env python
import logging
from langchain_community.llms import Ollama
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory


logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class LLM:
    def __init__(
        self,
        model_name: str = "mistral",
        temperature: float = 0.5,
        callbacks=None,
        knowledge_base: str = "None",
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
        self.set_knowledge_base(knowledge_base)
        # for dynamic RAG
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
            logger.debug(f"Using RAG with {self.model_name}")
            return RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_db.as_retriever(),
                memory=self.memory,
            )
        else:
            logger.debug(f"Using LLM: {self.model_name}")
            return self.llm

    def set_knowledge_base(self, kb_name: str):
        """Set the knowledge base for the RAG model.

        Parameters
        ----------
        kb_name : str
            The name of the knowledge base.
        """
        if kb_name == "None":
            logger.debug("No knowledge base selected")
            self.vector_db = None
        else:
            logger.debug(f"Loading knowledge base: {kb_name}")
            kb_path = f"vectorDB/{kb_name.lower()}"
            self.vector_db = Chroma(
                persist_directory=kb_path,
                embedding_function=self.embeddings,
            )

    def set_model(self, model_name: str):
        """Set the model to use.

        Parameters
        ----------
        model_name : str
            The name of the model to use.
        """
        logger.debug(f"Setting model to {model_name}")
        self.model_name = model_name
        self.llm = Ollama(
            model=model_name,
            callbacks=[self.callback],
        )

    def set_callbacks(self, callbacks):
        self.callback = callbacks
        self.llm.callbacks = [self.callback]

    def set_temperature(self, temperature: float):
        """Set the temperature for the model.

        Parameters
        ----------
        temperature : float
            The temperature to set.
        """
        logger.debug(f"Setting temperature to {temperature}")
        self.llm.temperature = temperature

    def update_vectordb(self, new_file: str):
        """Load the new file into the vector database.

        Parameters
        ----------
        new_file : str
            The path to the new file.
        """
        logger.debug(f"Updating vector database with {new_file}")
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
