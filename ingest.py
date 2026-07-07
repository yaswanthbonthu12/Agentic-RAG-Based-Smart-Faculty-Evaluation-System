import os
import time
import pandas as pd
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from pinecone_text.sparse import BM25Encoder


load_dotenv()

pc = Pinecone(api_key="pinecone_API_KEY")

INDEX_NAME = "lecturer-feedback"


existing_indexes = [idx.name for idx in pc.list_indexes()]

if INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=INDEX_NAME,
        dimension=1024,
        metric="dotproduct",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

    while not pc.describe_index(INDEX_NAME).status["ready"]:
        print("Waiting for index...")
        time.sleep(2)

index = pc.Index(INDEX_NAME)

print("Connected to Pinecone")


df = pd.read_csv(r"C:\Users\hp\RAG\pinecone_venv\feedback.csv")




documents = []

for _, row in df.iterrows():

    documents.append(
        Document(
            page_content=f"""
Lecturer: {row['lecture_name']}
Subject: {row['subject_name']}
Subject Type: {row['lecture_type']}
Semester: {row['semester']}
Rating: {row['student_rating']}

Student Feedback:
{row['student_comment']}
""".strip(),

            metadata={
                "lecture_id": row["lecture_id"],
                "lecture_name": row["lecture_name"],
                "subject": row["subject_name"],
                "subject_type": row["lecture_type"],
                "semester": int(row["semester"]),
                "rating": int(row["student_rating"])
            }
        )
    )

print("Documents created")

# -----------------------------
# Embedding Model
# -----------------------------
embeddings = OllamaEmbeddings(
    model="mxbai-embed-large"
)

# -----------------------------
# BM25
# -----------------------------
texts = [doc.page_content for doc in documents]

bm25 = BM25Encoder()

bm25.fit(texts)

bm25.dump("bm25.json")

print("BM25 created")

sparse_vectors = bm25.encode_documents(texts)

print("Sparse vectors created")

# -----------------------------
# Dense Embeddings
# -----------------------------
dense_vectors = []

EMBED_BATCH = 20      # Use 20 or 25 if Ollama crashes

for start in range(0, len(texts), EMBED_BATCH):

    end = min(start + EMBED_BATCH, len(texts))

    print(f"Embedding {start} - {end}")

    batch = texts[start:end]

    try:

        vectors = embeddings.embed_documents(batch)

        dense_vectors.extend(vectors)

    except Exception as e:

        print(f"Embedding failed at batch {start}-{end}")

        raise e

print("Dense vectors created")

# -----------------------------
# Prepare Pinecone Vectors
# -----------------------------
vectors = []

for i, doc in enumerate(documents):

    vectors.append(
        {
            "id": f"{doc.metadata['lecture_id']}_{i}",
            "values": dense_vectors[i],
            "sparse_values": sparse_vectors[i],
            "metadata": {
                **doc.metadata,
                "text": doc.page_content
            }
        }
    )

print("Vectors prepared")

# -----------------------------
# Upload
# -----------------------------
UPLOAD_BATCH = 100

for start in range(0, len(vectors), UPLOAD_BATCH):

    end = min(start + UPLOAD_BATCH, len(vectors))

    print(f"Uploading {start} - {end}")

    index.upsert(
        vectors=vectors[start:end]
    )

print("\nUpload Completed Successfully")

print(index.describe_index_stats())