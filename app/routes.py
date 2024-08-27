import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.models import Query, JobPosting
from app.utils import (
    process_query,
    process_pdf_query,
    process_job_query,
    save_and_process_pdf,
    get_documents_in_database,
    clear_database,
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
    try:
        if not os.path.exists(pdf_folder_path):
            raise Exception("PDF storage folder does not exist")
        
        pdf_directory = "pdf"
        if not os.path.exists(pdf_directory):
            raise Exception("PDF upload directory does not exist")
        
        test_query = "Test query"
        process_query(test_query)
        process_pdf_query(test_query)
        
        try:
            os.listdir(pdf_directory)
        except Exception as e:
            raise Exception(f"Cannot access PDF directory: {str(e)}")
        
        return JSONResponse(content={"status": "healthy", "message": "All systems operational"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "unhealthy", "message": f"Healthcheck failed: {str(e)}"}, status_code=500)

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
async def query_pdf_post(query: Query):
    result, sources = process_pdf_query(query.query, query.include_sources)
    
    if query.include_sources:
        return JSONResponse(content={"answer": result, "sources": sources})
    else:
        return JSONResponse(content={"answer": result})

@router.post("/clear_database", tags=["Documents"])
async def clear_db():
    try:
        result = clear_database()
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
async def query_jobs_post(query: Query):
    result, sources = process_job_query(query.query, query.include_sources)
    
    if query.include_sources:
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