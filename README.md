# Job Search Assistant API

## Overview

This project is a FastAPI-based web service that provides job search functionality. It includes features for scraping job postings, storing them in a vector database (ChromaDB), and querying the database for relevant job information. The service also supports PDF document uploading and querying.

## Features

- Scrape and store job postings with assigned serial numbers
- Query job postings using natural language
- Upload and query PDF documents
- Retrieve specific job postings by serial number
- Clear database and uploaded PDFs

## Technologies Used

- FastAPI
- ChromaDB
- LangChain
- Ollama (for LLM integration)
- Pydantic
- uvicorn

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/swolfyguy/pdf2vector-api.git
   cd pdf2vector-api
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Make sure you have Ollama installed and running with the `llama3.1` model available.

5. Make sure that the Ollama server is running.
   ```
   ollama serve
   ```

## Usage

1. Start the FastAPI server:
   ```
   python main.py
   ```

2. The API will be available at `http://localhost:8080`. You can access the interactive API documentation at `http://localhost:8080/docs`.

## API Endpoints

- `GET /healthcheck`: Check the health status of the API
- `GET /show_documents`: List all documents in the database
- `POST /upload_pdf`: Upload a PDF document
- `POST /query_pdf`: Query uploaded PDF documents
- `POST /clear_database`: Clear the database and delete uploaded PDFs
- `GET /data`: Scrape and store job postings
- `POST /query_jobs`: Query stored job postings
- `GET /job/{serial_number}`: Retrieve a specific job posting by serial number

## Project Structure

- `main.py`: Entry point of the application
- `app/routes.py`: API route definitions
- `app/models.py`: Pydantic model definitions
- `app/utils.py`: Utility functions for processing queries and managing the database
- `scrape/scraper.py`: Job scraping functionality (not included in the provided files)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.