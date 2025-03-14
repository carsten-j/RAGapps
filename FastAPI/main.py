from fastapi import FastAPI
from fastembed import SparseEmbedding, SparseTextEmbedding
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    NamedSparseVector,
    SearchRequest,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

app = FastAPI()


collection_name = "PDFs"

client = QdrantClient("qdrant:6333")

exist = client.collection_exists(collection_name=collection_name)

if not exist:
    client.create_collection(
        collection_name,
        vectors_config={
            "text-dense": VectorParams(
                size=1024,
                distance=Distance.COSINE,
            )
        },
        sparse_vectors_config={
            "text-sparse": SparseVectorParams(
                index=SparseIndexParams(
                    on_disk=False,
                )
            )
        },
    )


sparse_model_name = "Qdrant/bm25"
sparse_model = SparseTextEmbedding(model_name=sparse_model_name, batch_size=32)


class CreateEmbedding(BaseModel):
    embedding: str


def make_sparse_embedding(texts: list[str]) -> list[SparseEmbedding]:
    return list(sparse_model.embed(texts, batch_size=256))


def search(query_text: str):
    query_sparse_vectors: list[SparseEmbedding] = make_sparse_embedding([query_text])

    search_results = client.search_batch(
        collection_name=collection_name,
        requests=[
            SearchRequest(
                vector=NamedSparseVector(
                    name="text-sparse",
                    vector=SparseVector(
                        indices=query_sparse_vectors[0].indices.tolist(),
                        values=query_sparse_vectors[0].values.tolist(),
                    ),
                ),
                limit=10,
                with_payload=True,
            ),
        ],
    )

    return search_results


@app.get("/query/{text}")
async def query_text(text: str):
    """
    Endpoint that takes a query text and returns hits.
    """
    hits = search(text)

    return {"hits": hits}


# @app.post("/embedding/")
# async def create_item(embedding: CreateEmbedding):
#     return embedding.embedding
