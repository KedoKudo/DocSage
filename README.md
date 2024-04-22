# DocSage
A document analyzer backed by local Large Language Models (LLMs).

## How to use

- Install the backend, `Ollama`. On Mac, it is recommended to use `homebrew` to install `Ollama`:
```bash
brew install ollama
```

- Make sure to start the `Ollam` server:
```bash
brew service start ollama
```

- Create a new virtual environment and install the required packages with `environment.yml`

- Install `DocSage` as a package:
```bash
pip install -e .
```

- Start the webapp with the following command:
```bash
streamlit run ollama_rag_streamlit.py
```

## Additional Information

To learn more about the retrieval-augmented generation (RAG) model used here, please go through the notebooks in the `notebooks` directory.

## License

See the [LICENSE](LICENSE) file for license rights and limitations (MIT).
