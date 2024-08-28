import os
import shutil
from app.models import JobPosting
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pdf_processing import extract_text_from_pdf, generate_embeddings, store_embeddings

pdf_folder_path = "db_pdf"
scrape_folder_path = "db_scrape"
cached_llm = Ollama(model="llama3.1")

raw_prompt = PromptTemplate.from_template(
    """ 
    <s>[INST] You are a technical assistant, good at searching documents. If you do not have an answer from the provided information, say so. [/INST] </s>
    [INST] {input}
            Context: {context}
            Answer:
    [/INST]
"""
)

job_query_prompt = PromptTemplate.from_template(
    """ 
    <s>[INST] You are a job search assistant, skilled at finding relevant job postings. If you do not have an answer from the provided information, say so. Always include the Serial Number of relevant job postings in your answer. [/INST] </s>
    [INST] {input}
            Context: {context}
            Answer:
    [/INST]
"""
)

def process_query(query: str) -> str:
    return cached_llm.invoke(query)

def process_pdf_query(query: str, include_sources: bool = False):
    embedding = FastEmbedEmbeddings()
    vector_store = Chroma(persist_directory=pdf_folder_path, embedding_function=embedding)
    
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 20,
            "score_threshold": 0.1,
        },
    )
    
    document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
    chain = create_retrieval_chain(retriever, document_chain)
    
    result = chain.invoke({"input": query})
    
    if include_sources:
        sources = [
            {"source": doc.metadata["source"], "page_content": doc.page_content}
            for doc in result["context"]
        ]
        return result["answer"], sources
    else:
        return result["answer"], None

def process_job_query(query: str, include_sources: bool = False):
    embedding = FastEmbedEmbeddings()
    vector_store = Chroma(persist_directory=scrape_folder_path, embedding_function=embedding)
    
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5,
            "score_threshold": 0.5,
        },
    )
    
    document_chain = create_stuff_documents_chain(cached_llm, job_query_prompt)
    chain = create_retrieval_chain(retriever, document_chain)
    
    result = chain.invoke({"input": query})
    
    if include_sources:
        sources = [
            {
                "source": doc.metadata["source"],
                "job_id": doc.metadata.get("job_id"),
                "serial_number": doc.metadata.get("serial_number"),
                "page_content": doc.page_content
            }
            for doc in result["context"]
        ]
        return result["answer"], sources
    else:
        return result["answer"], None

def save_and_process_pdf(file):
    file_name = file.filename
    save_file = f"pdf/{file_name}"
    
    try:
        with open(save_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise Exception(f"Could not save file: {str(e)}")
    
    chunks = extract_text_from_pdf(save_file)
    embedding, chunks = generate_embeddings(chunks)
    vector_store = store_embeddings(embedding, chunks, pdf_folder_path)
    
    return {
        "status": "Successfully Uploaded",
        "filename": file_name,
        "doc_len": len(chunks),
        "chunks": len(chunks)
    }

def get_documents_in_database():
    embedding = FastEmbedEmbeddings()
    vector_store = Chroma(persist_directory=pdf_folder_path, embedding_function=embedding)
    
    documents = vector_store.get()
    
    unique_sources = set()
    for metadata in documents['metadatas']:
        if 'source' in metadata:
            source = metadata['source']
            filename = os.path.basename(source)
            unique_sources.add(filename)
    
    return list(unique_sources)

def clear_pdf_database():
    embedding = FastEmbedEmbeddings()
    
    # Clear PDF database
    vector_store_pdf = Chroma(persist_directory=pdf_folder_path, embedding_function=embedding)
    vector_store_pdf.delete_collection()
    vector_store_pdf = Chroma(persist_directory=pdf_folder_path, embedding_function=embedding)
    vector_store_pdf.persist()
    
    # Delete all PDFs in the "pdf" directory
    pdf_directory = "pdf"
    if os.path.exists(pdf_directory):
        for filename in os.listdir(pdf_directory):
            file_path = os.path.join(pdf_directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    
    return {"message": "PDF database cleared and PDFs deleted successfully"}

def clear_scrape_database():
    embedding = FastEmbedEmbeddings()
    
    # Clear scraped data database
    vector_store_scrape = Chroma(persist_directory=scrape_folder_path, embedding_function=embedding)
    vector_store_scrape.delete_collection()
    vector_store_scrape = Chroma(persist_directory=scrape_folder_path, embedding_function=embedding)
    vector_store_scrape.persist()
    
    return {"message": "Scraped job database cleared successfully"}