from enum import Enum

class VectorDBEnum(Enum):
    QDRANT= "QDRANT"
    PGVECTOR = "PGVECTOR"

class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"
    EUCLID="Euclidean"

class PgVectorTableSchemeEnums(Enum):
    ID = 'id'
    TEXT = 'text'
    VECTOR = 'vector'
    CHUNK_ID = 'chunk_id'
    METADATA = 'metadata'
    _PREFIX = 'pgvector'

class PgVectorDistanceMethodEnums(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"
    
class PgVectorIndexTypeEnums(Enum):
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"