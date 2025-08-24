from abc import ABC, abstractmethod
from typing import List
from src.models.db_schemes import RetrievedDocument

class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def create_collection(self, collection_name: str,embedding_size,
                          do_rest=False):
        pass

    @abstractmethod
    def insert_one(self,collection_name,text:str,vector:list,metadata:dict=None,
                   record_id:str=None):
        pass

    @abstractmethod
    def insert_many(self, collection_name: str, texts: list,
                    vectors: list, metadata: list = None,
                    record_ids: list = None, batch_size: int = 50):
        pass

    @abstractmethod
    def search_by_vector(self,collection_name: str,vector:list,limit: int)->List[RetrievedDocument]:
        pass




