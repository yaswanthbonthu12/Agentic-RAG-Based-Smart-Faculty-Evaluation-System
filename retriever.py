from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from pinecone_text.sparse import BM25Encoder
from langchain_cohere import CohereRerank



pc = Pinecone(api_key="pinecone_API_KEY")

index = pc.Index("lecturer-feedback")


bm25 = BM25Encoder().load("bm25.json")

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

reranker = CohereRerank(
    cohere_api_key="cohere_API_KEY",
    model="rerank-english-v3.0",
    top_n=5
)

def retrieve(query,filters=None,top_k=20):


   

    dense_query = embeddings.embed_query(query)


   


    sparse_query = bm25.encode_queries(query)




    results = index.query(
        vector=dense_query,
        sparse_vector=sparse_query,
        top_k=top_k,
        include_metadata=True,
         filter=filters )
        




    docs = [
        Document(
            page_content=x["metadata"]["text"],
            metadata=x["metadata"]
        )
        for x in results["matches"]
    ]

    return reranker.compress_documents(
        documents=docs,
        query=query
    )
    


  
