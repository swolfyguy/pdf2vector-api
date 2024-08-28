import os
from fastapi import APIRouter, File, UploadFile, HTTPException, Query as QueryParam
from fastapi.responses import JSONResponse
from app.models import Query, JobPosting
from app.utils import (
    process_query,
    process_pdf_query,
    process_job_query,
    save_and_process_pdf,
    get_documents_in_database,
    clear_pdf_database,
    clear_scrape_database,
    pdf_folder_path,
    scrape_folder_path,
)
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from scrape.scraper import get_all_jobs

router = APIRouter()

@router.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    health_status = {
        "status": "healthy",
        "checks": {}
    }

    try:
        # Check PDF storage folder
        if not os.path.exists(pdf_folder_path):
            raise Exception("PDF storage folder does not exist")
        health_status["checks"]["pdf_storage"] = "OK"

        # Check PDF upload directory
        pdf_directory = "pdf"
        if not os.path.exists(pdf_directory):
            raise Exception("PDF upload directory does not exist")
        health_status["checks"]["pdf_upload"] = "OK"

        # Check if we can list files in PDF directory
        try:
            os.listdir(pdf_directory)
            health_status["checks"]["pdf_directory_access"] = "OK"
        except Exception as e:
            health_status["checks"]["pdf_directory_access"] = f"Error: {str(e)}"

        # Test query processing
        test_query = "Test query"
        process_query(test_query)
        health_status["checks"]["query_processing"] = "OK"

        # Test PDF query processing
        process_pdf_query(test_query)
        health_status["checks"]["pdf_query_processing"] = "OK"

        # Check ChromaDB for PDF
        try:
            embedding = FastEmbedEmbeddings()
            Chroma(persist_directory=pdf_folder_path, embedding_function=embedding)
            health_status["checks"]["chromadb_pdf"] = "OK"
        except Exception as e:
            health_status["checks"]["chromadb_pdf"] = f"Error: {str(e)}"

        # Check ChromaDB for scraped data
        try:
            Chroma(persist_directory=scrape_folder_path, embedding_function=embedding)
            health_status["checks"]["chromadb_scrape"] = "OK"
        except Exception as e:
            health_status["checks"]["chromadb_scrape"] = f"Error: {str(e)}"

        return JSONResponse(content=health_status, status_code=200)
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        return JSONResponse(content=health_status, status_code=500)

@router.get("/show_documents", tags=["Documents"])
async def show_documents():
    try:
        documents = get_documents_in_database()
        return JSONResponse(content={"documents": documents})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_pdf", tags=["Documents"])
async def pdf_post(file: UploadFile = File(...)):
    try:
        result = save_and_process_pdf(file)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query_pdf", tags=["Documents"])
async def query_pdf_post(
    query: Query,
    include_sources: bool = QueryParam(False, description="Include sources in the response")
):
    result, sources = process_pdf_query(query.query, include_sources)
    
    if include_sources:
        return JSONResponse(content={"answer": result, "sources": sources})
    else:
        return JSONResponse(content={"answer": result})

@router.post("/clear_database", tags=["Documents"])
async def clear_pdf_db():
    try:
        result = clear_pdf_database()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data", tags=["Scraper"])
async def scraped_data() -> dict:
    try:
        jobs = get_all_jobs()
        
        # Process and store jobs in ChromaDB
        embedding = FastEmbedEmbeddings()
        vector_store = Chroma(persist_directory=scrape_folder_path, embedding_function=embedding)
        
        documents = []
        for index, job in enumerate(jobs, start=1):
            # Ensure job is a dictionary and has all required keys
            if isinstance(job, dict) and all(key in job for key in ['job_title', 'posted_on', 'description', 'job_data', 'link']):
                job_data_str = ' '.join([f"- {feature.get('Title', '')}: {feature.get('Description', '')}" for feature in job['job_data'] if isinstance(feature, dict)])
                text = f"""
                Serial Number: {index}
                Job Title: {job['job_title']}
                Posted On: {job['posted_on']}
                Description: {job['description']}
                Job Data:
                {job_data_str}
                Link: {job['link']}
                """
                doc = Document(page_content=text, metadata={"source": job['link'], "job_id": job.get('id', ''), "serial_number": index})
                documents.append(doc)
                
                # Add serial number to the job dictionary
                job['serial_number'] = index
            else:
                print(f"Skipping invalid job entry: {job}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
        )
        chunks = text_splitter.split_documents(documents)
        
        vector_store.add_documents(chunks)
        vector_store.persist()
        
        return {
            "message": "Data has been successfully stored in ChromaDB",
            "jobs": jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query_jobs", tags=["Jobs"])
async def query_jobs_post(
    query: Query,
    include_sources: bool = QueryParam(False, description="Include sources in the response")
):
    result, sources = process_job_query(query.query, include_sources)
    
    if include_sources:
        return JSONResponse(content={"answer": result, "sources": sources})
    else:
        return JSONResponse(content={"answer": result})

@router.get("/job/{serial_number}", tags=["Jobs"])
async def get_job_by_serial(serial_number: int):
    try:
        embedding = FastEmbedEmbeddings()
        vector_store = Chroma(persist_directory=scrape_folder_path, embedding_function=embedding)
        
        results = vector_store.similarity_search(
            f"Serial Number: {serial_number}",
            k=1,
            filter={"serial_number": serial_number}
        )
        
        if results:
            job_data = results[0].page_content
            return JSONResponse(content={"job_data": job_data})
        else:
            raise HTTPException(status_code=404, detail=f"Job with serial number {serial_number} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear_database_scrape", tags=["Jobs"])
async def clear_scrape_db():
    try:
        result = clear_scrape_database()
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))