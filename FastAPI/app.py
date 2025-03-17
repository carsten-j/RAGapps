import os

import qdrant_client
import requests
from fastembed import SparseEmbedding, SparseTextEmbedding
from pydantic import BaseModel
from qdrant_client.models import (
    Distance,
    NamedSparseVector,
    PointStruct,
    SearchRequest,
    SparseIndexParams,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from fastapi import FastAPI

# https://blog.futuresmart.ai/building-an-async-similarity-search-system-from-scratch-with-fastapi-and-qdrant-vectordb


class QueryRequest(BaseModel):
    query: str  # The search query entered by the user
    limit: int  # The number of search results to return


class UploadRequest(BaseModel):
    points: list[PointStruct]  # The search query entered by the user
    batch_size: int  # The number of search results to return


class UploadRequest2(BaseModel):
    points: list[str]  # The search query entered by the user
    batch_size: int  # The number of search results to return


collection_name = "FOO"

sparse_model_name = "Qdrant/bm25"
sparse_model = SparseTextEmbedding(model_name=sparse_model_name, batch_size=32)

# Initialize Qdrant client
qdrant = qdrant_client.AsyncQdrantClient("http://localhost:6333")


def make_sparse_embedding(texts: list[str]) -> list[SparseEmbedding]:
    return list(sparse_model.embed(texts, batch_size=256))


# Create collection in Qdrant vector database
async def create_qdrant_collection():
    exist = await qdrant.collection_exists(collection_name=collection_name)
    if not exist:
        await qdrant.create_collection(
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


async def qdrant_search(query: str, limit: int):
    # # Compute sparse and dense vectors
    query_sparse_vectors: list[SparseEmbedding] = make_sparse_embedding([query])

    search_results = await qdrant.search_batch(
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
                limit=limit,
                with_payload=True,
            ),
        ],
    )

    results = [
        {
            "id": res.id,
            "page": res.payload["page"],
            "source": res.payload["source"],
            "text": res.payload["text"],
            "score": res.score,  # Semantic similarity score
        }
        for res in search_results
    ]

    return results


# FastAPI lifecycle event to initialize Qdrant
async def async_lifespan(app: FastAPI):
    await create_qdrant_collection()  # Ensures the Qdrant collection exists
    # await read_and_store_data("vehicle.csv", qdrant)  # Load initial data
    yield  # Yield control, FastAPI will now handle incoming requests


app = FastAPI(lifespan=async_lifespan)


def restore_snapshot():
    # snapshot_path = "/mnt/data/"
    file_name = (
        "/Users/carsten/Downloads/PDFs-3018529611761135-2025-03-13-19-10-01.snapshot"
    )
    requests.post(
        "http://localhost:6333/collections/foobar/snapshots/upload?priority=snapshot",
        files={"snapshot": open(file_name, "rb")},
    )


def read_file_from_share(file_path: str) -> int:
    """
    Reads and returns the contents of a file from the mounted Azure File Share.
    """
    if not os.path.exists(file_path):
        return -1

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return len(content)


@app.get("/")
async def read_root():
    return {"message": "Hello, Qdrant!"}


@app.get("/test")
def test():
    restore_snapshot()
    return {"message": "Snapshot restored!"}
    # result = read_file_from_share("/mnt/data/test.txt")
    # return {"message": result}


# @app.post("/upload")
# async def upload(upload_request: UploadRequest):
#     for i in range(0, len(upload_request.points), upload_request.batch_size):
#         batch = upload_request.points[i : i + upload_request.batch_size]
#         updateResult = await qdrant.upsert(collection_name, batch)

#     return {"result": updateResult}


# @app.post("/upload2")
# async def upload2(upload_request: UploadRequest2):
#     updateResult = len(upload_request.points) + upload_request.batch_size

#     return {"result": updateResult}


@app.post("/semantic_search")
async def search(query_request: QueryRequest):
    results = await qdrant_search(query_request.query, query_request.limit)
    return {"results": results}
