from ..Interface_LLM import Interface_LLM
from ..Enums_LLM import CoHereEnums, DocumentTypeEnum
import cohere
import logging
from typing import List, Union


class CoHereProvider(Interface_LLM):

    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)

        self.enums = CoHereEnums

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_dimensions_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_dimensions_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                      temperature: float = None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            temperature=temperature,
            max_tokens=max_output_tokens
        )

        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None

        return response.text


    def embed_text(self, text: Union[str,List[str]], document_type: str = None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if isinstance(text, str):
            text = [text]

        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None

        input_type=CoHereEnums.DOCUMENT.value
        if document_type in {DocumentTypeEnum.QUERY, DocumentTypeEnum.QUERY.value}:
            input_type = CoHereEnums.QUERY

        try:
            resp = self.client.embed(
                model=self.embedding_model_id,
                texts=[ self.process_text(t) for t in text ],
                input_type=input_type,
                embedding_types=["float"],  # fine to keep
            )
        except Exception as exc:
            self.logger.exception("Cohere embed failed: %s", exc)
            return None

        vectors = getattr(resp.embeddings, "float", None)  # list of vectors

        # (optional) fallback for old Bedrock / ≤4.0 list‑only schema
        if vectors is None and isinstance(resp.embeddings, list):
            vectors = resp.embeddings

        if not vectors:  # now OK: this really is a list
            self.logger.error("No embeddings returned from Cohere")
            return None

        return vectors


    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": prompt
        }