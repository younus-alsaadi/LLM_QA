from ..Interface_LLM import Interface_LLM
from ..Enums_LLM import OpenAIEnums
from openai import OpenAI
import logging
import httpx

class OpenAIProvider(Interface_LLM):
    def __init__(self,  api_key: str, api_url: str=None,
                        default_input_max_characters: int=500,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):

        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_dimensions_size = None
        http_client = httpx.Client(proxy="http://127.0.0.1:8080")  # httpx 0.27.x

        self.client = OpenAI(
            api_key=self.api_key,
            http_client=http_client,
            base_url=self.api_url if self.api_url and len(self.api_url) else None, # User OpenAPI or OLLAMA
        )

        self.enums = OpenAIEnums

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str): # for change the model type in the runtime
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_dimensions_size: int):
        self.embedding_model_id = model_id
        self.embedding_dimensions_size = embedding_dimensions_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                      temperature: float = None):

        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
        self.construct_prompt(prompt=prompt,role=OpenAIEnums.USER.value)
        )
        response=self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None

        return response.choices[0].message.content


    def embed_text(self, text: str, document_type: str = None):


        if not self.client or not self.embedding_model_id:
            self.logger.error("OpenAI client/model not set")
            return None

        kwargs = {"model": self.embedding_model_id, "input": text}

        # Only v3 models support custom dimensions
        if self.embedding_dimensions_size and self.embedding_model_id.startswith("text-embedding-3"):
            kwargs["dimensions"] = int(self.embedding_dimensions_size)

        response=self.client.embeddings.create(model=self.embedding_model_id,input=text)

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None

        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str):

        return {
            "role": role,
            'content': prompt,
        }



