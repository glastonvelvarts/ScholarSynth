from pymilvus import Collection
from papercontext.vectorstore import client
client.connect_to_milvus()
collection = Collection("papersynth")
collection.load()

results = collection.query(
    expr='chunk_id != ""',
    output_fields=[
        "chunk_id",
        "document_name",
        "page",
        "text"
    ],
    limit=5
)

for row in results:
    print("\n")
    print(row)