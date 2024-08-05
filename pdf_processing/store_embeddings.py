import chromadb

def store_embeddings_in_chroma(embeddings, text):
    client = chromadb.Client()
    collection = client.create_collection("pdf_embeddings")
    collection.add(documents=[text], embeddings=[embeddings], ids=["doc1"])
