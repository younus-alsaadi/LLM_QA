from .BaseController import BaseController
from src.models.db_schemes import Project, DataChunk
import json
from typing import List
from ..stores.llms.Enums_LLM import DocumentTypeEnum

class NLPController(BaseController):

    def __init__(self, vectordb_client, generation_client,
                 embedding_client,template_parser):
        super().__init__()

        self.vector_db_client = vectordb_client
        self.generation_model_client = generation_client
        self.embedding_model_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{self.vector_db_client.default_vector_size}_{project_id}".strip()

    async def rest_vector_db_collection(self,project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vector_db_client.delete_collection(collection_name=collection_name)

    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = await self.vector_db_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )

    async def index_into_vector_db(self,project: Project,chunks:List[DataChunk], chunks_ids: List[int],
                             do_reset: int = False):

        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: manges items
        chunks_as_text=[c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = self.embedding_model_client.embed_text(text=chunks_as_text,
                                                   document_type=DocumentTypeEnum.DOCUMENT.value)
        # step3: create collection if not exists

        _=await self.vector_db_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_model_client.embedding_dimensions_size,
            do_reset=do_reset,
        )


        # step4: insert into vector db
        _=await self.vector_db_client.insert_many(
            collection_name=collection_name,
            texts=chunks_as_text,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True


    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):

        # step1: get collection name
        query_vector = None
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: get text embedding vector
        vectors = self.embedding_model_client.embed_text(text=text,
                                                 document_type=DocumentTypeEnum.QUERY.value)



        if not vectors or len(vectors) == 0:
            return False

        if isinstance(vectors, list) and len(vectors) > 0:
            query_vector = vectors[0]

        if not query_vector:
            return False

            # step3: do semantic search
        results = await self.vector_db_client.search_by_vector(
                collection_name=collection_name,
                vector=query_vector,
                limit=limit
        )

        if not results:
            return False

        return results

    async def answer_rag_question(self, project: Project, query: str, limit: int = 10):

        answer, full_prompt, chat_history = None, None, None
        # step1: retrieve related documents
        retrieved_documents = await self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
        )
        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history

        # step2: Construct LLM prompt
        system_prompt=self.template_parser.get_template_from_locales("rag","system_prompt")

        documents_prompts="\n".join([
            self.template_parser.get_template_from_locales("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": self.generation_model_client.process_text(doc.text)
            })
            for idx,doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get_template_from_locales("rag", "footer_prompt", {
            "query": query
        })
        # step3: Construct Generation Client Prompts

        chat_history=[
            self.generation_model_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_model_client.enums.SYSTEM.value
            )
        ]

        full_prompt="\n\n".join([documents_prompts,footer_prompt])

        answer_from_generation_model=self.generation_model_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer_from_generation_model, full_prompt, chat_history











