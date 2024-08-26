from pydantic import BaseModel
from typing import List, Dict, Optional

class Query(BaseModel):
    query: str
    include_sources: bool = False

class Feature(BaseModel):
    Title: str
    Description: str

class JobPosting(BaseModel):
    job_title: str
    posted_on: str
    location: str
    description: str
    job_data: List[Dict[str, str]]
    link: str

class ScrapedData(BaseModel):
    jobs: List[JobPosting]

class TextInput(BaseModel):
    job_posting: JobPosting