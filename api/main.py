
import uuid
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from pdf_processing.extract_text import extract_text_from_pdf
import chromadb

load_dotenv()
app = FastAPI()
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class Document(BaseModel):
    text: str

@app.on_event("startup")
async def startup():
    host = os.getenv("HOST")
    print(f"host {host}")
    global chroma_client
    chroma_client = chromadb.HttpClient(host)


@app.post("/create_collection/{collection_name}")
async def create_collection(collection_name: str):
    try:
        chroma_collection = chroma_client.create_collection(collection_name)
        return {"message": f"Collection '{chroma_collection}' created successfully."}
    except Exception as e:
        return {"error": f"Error creating collection: {str(e)}"}


@app.post("/add_documents/{collection_name}")
async def add_documents(collection_name: str, file: UploadFile = File(...)):
    try:
        collection = chroma_client.get_collection(collection_name)
        if collection is None:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found.")
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted.")

        # Create a file path for saving the file
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save the uploaded file to the specified directory
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the file if needed (e.g., extract text)
        document_texts = extract_text_from_pdf(file_path)
        # document_texts = text
        # print(document_texts)
        document_ids = [str(uuid.uuid4()) for _ in
                        range(len(document_texts))]
        print(document_ids)  # Generate the same number of IDs as the number of documents
        collection.add(documents=document_texts, ids=document_ids)
        return {"message": "Documents added to collection successfully."}
    except Exception as e:
        raise {"error": f"Error adding documents: {str(e)}"}


@app.get("/AllCollections")
async def query_collection():
    collections = chroma_client.list_collections()
    return {"collections": [collection.name for collection in collections]}


@app.get("/query/{collection_name}")
async def query_collection(collection_name: str, query: str):
    try:
        collection = chroma_client.get_collection(collection_name)
        if collection is None:
            raise HTTPException(status_code=404, detail=f"Collection '{collection_name}' not found.")
        results = collection.query(
            query_texts=[query],  # Chroma will embed this for you
            n_results=1,  # how many results to return
            include=["embeddings", "documents", "distances"]
        )
        # document_texts = [result.documents[0].text for result in results.results]
        return JSONResponse({"results": results["documents"]})
    except Exception as e:
        return {"error": f"Error querying collection: {str(e)}"}


@app.delete("/clear_database")
async def clear_database(collection_name: str,):
    try:
        collections = chroma_client.list_collections()
        if collection_name not in collections:
            return {"message": f"All {collection_name} not found"}
        chroma_client.delete_collection(collection_name)
        return {"message": f"All collections deleted successfully. {collections}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")


#
# @app.post("/upload/")
# async def upload_pdf(file: UploadFile = File(...)):
#     if file.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are accepted.")
#
#     # Create a file path for saving the file
#     file_path = os.path.join(UPLOAD_DIR, file.filename)
#
#     # Save the uploaded file to the specified directory
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#
#     # Process the file if needed (e.g., extract text)
#     text = extract_text_from_pdf(file_path)
#
#     # You can do more processing here, such as generating embeddings, etc.
#
#     return JSONResponse(content={"filename": file.filename, "extracted_text": text})

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
