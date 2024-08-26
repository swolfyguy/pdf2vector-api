# fetch_and_store.py
import requests
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.models import ScrapedData, JobPosting

# Constants
API_ENDPOINT = "http://your-api-url/scraped_data"
CHROMA_PERSIST_DIRECTORY = "db"

def fetch_data() -> ScrapedData:
    response = requests.get(API_ENDPOINT)
    response.raise_for_status()
    return ScrapedData(jobs=[JobPosting(**job) for job in response.json()])

def process_job_posting(job: JobPosting) -> Document:
    text = f"""
    Job Title: {job.job_title}
    Posted On: {job.posted_on}
    Location: {job.location}
    Description: {job.description}
    Features:
    {' '.join([f'- {feature["Title"]}: {feature["Description"]}' for feature in job.job_data])}
    Link: {job.link}
    """
    return Document(page_content=text, metadata={"source": job.link})

def store_in_chroma(documents: List[Document]):
    embedding = FastEmbedEmbeddings()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
    )
    chunks = text_splitter.split_documents(documents)
    
    vector_store = Chroma(persist_directory=CHROMA_PERSIST_DIRECTORY, embedding_function=embedding)
    vector_store.add_documents(chunks)
    vector_store.persist()
    
    return len(chunks)

def main():
    try:
        scraped_data = fetch_data()
        documents = [process_job_posting(job) for job in scraped_data.jobs]
        chunks_stored = store_in_chroma(documents)
        print(f"Successfully stored {chunks_stored} chunks in Chroma database.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()