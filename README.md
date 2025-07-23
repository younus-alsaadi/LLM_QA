# LLM_QA_RAG

This is a minimal implementation of the Retrieval-Augmented Generation (RAG) model for question answering.

## Requirements

- Python 3.8 or later

### Install Python using MiniConda

1. Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2. Create a new environment:
   ```bash
   conda create -n mini-rag python=3.8
3) Activate the environment:
    ```bash
    $ conda activate mini-rag
   
## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

## Run Docker Compose Services

```bash
$ cd docker
$ cp .env.example .env
```

- update `.env` with your credentials



```bash
$ cd docker
$ sudo docker compose up -d
```

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## POSTMAN Collection

Download the POSTMAN collection from [/assets/mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json)