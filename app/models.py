from pydantic import BaseModel
from typing import List, Optional

class Query(BaseModel):
    query: str
    include_sources: bool = False

class Feature(BaseModel):
    Title: str
    Description: str

class JobPosting(BaseModel):
    JobTitle: str
    PostedOn: str
    Location: str
    Description: str
    Features: List[Feature]

class TextInput(BaseModel):
    job_posting: JobPosting