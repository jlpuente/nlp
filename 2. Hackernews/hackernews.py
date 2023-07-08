import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

df = pd.read_json("./data/news.json", lines=True)
print(df.columns)
print(len(df.index))

df["title_article"] = df["headline"] + df["short_description"]

model = SentenceTransformer("average_word_embeddings_komninos")

qdrant = QdrantClient(":memory:")

qdrant.recreate_collection(
    collection_name="my_collection",
    vectors_config=VectorParams(size=300, distance=Distance.COSINE),
)

batch_size = 100

for i in tqdm(range(0, len(df.index), batch_size)):
    pos_final = min(i + batch_size, len(df.index))

    chunk = df.iloc[i:pos_final]

    xc = model.encode(chunk["title_article"].tolist())

    payload = chunk.to_dict(orient="records")

    qdrant.upsert(
        collection_name="my_collection",
        points=[
            PointStruct(
                id=idx,  # TODO: Do not repeat!
                vector=vector.tolist(), payload=payload[idx]
            ) for idx, vector in enumerate(xc)
        ]
    )

print(qdrant.count(collection_name="my_collection"))

user_history = df.loc[
    (df["category"] == "SPORTS") & (df["short_description"].str.contains("tennis"))
][:10]

user_embeddings = model.encode(user_history["title_article"].tolist()).tolist()
user = np.mean(user_embeddings, axis=0)

hits = qdrant.search(
    collection_name="my_collection",
    query_vector=user,
    limit=5,
)
for hit in hits:
    print(hit)
