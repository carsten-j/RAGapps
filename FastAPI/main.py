from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient, models

app = FastAPI()


strings_list = []

collection_name = "my_collection"

client = QdrantClient("localhost", port=6333)

exist = client.collection_exists(collection_name=collection_name)

if not exist:
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
            distance=models.Distance.COSINE,
        ),
    )


class StringRequest(BaseModel):
    content: str


class CreateEmbedding(BaseModel):
    embedding: str


@app.get("/query/{text}")
async def query_text(text: str):
    """
    Endpoint that takes a query text and returns hits.
    """
    hits = client.query_points(
        collection_name=collection_name,
        query=encoder.encode(text).tolist(),
        limit=3,
    ).points

    return {"hits": hits}


@app.post("/embedding/")
async def create_item(embedding: CreateEmbedding):
    return embedding.embedding


@app.post("/update_list")
def update_list(string_request: StringRequest):
    """Endpoint that accepts a string (via request body), appends it to the in-memory list, and returns the updated list."""
    strings_list.append(string_request.content)
    return {"all_strings": strings_list}
