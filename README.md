# PDF Processing and Querying System

This project is a FastAPI-based application that processes PDF documents, extracts text, generates embeddings, and stores them in a vector database (ChromaDB) for efficient querying.

## Features

- PDF text extraction
- Text embedding generation using OpenAI's API
- Storage of embeddings in ChromaDB
- RESTful API for document upload and querying
- Containerized application using Docker

## Prerequisites

- Docker and Docker Compose
- OpenAI API key

## Setup

1. Clone the repository:
git clone https://github.com/swolfyguy/pdf2vector-api
cd <project-directory>

2. Create a .env file in the project root and add your OpenAI API key:
OPENAI_API_KEY=your_api_key_here

3. Build and run the Docker containers:
docker-compose up --build

## Usage

The application will be available at http://localhost:8080. You can use the following endpoints:

- POST /create_collection/{collection_name}: Create a new collection
- POST /add_documents/{collection_name}: Upload a PDF file to a collection
- GET /AllCollections: List all collections
- GET /query/{collection_name}: Query a collection
- DELETE /clear_database: Clear the database

Use a tool like curl or Postman to interact with the API.

## Project Structure

- api/: Main application directory
- main.py: FastAPI application
- uploaded_files/: Directory for uploaded PDFs
- pdf_processing/: PDF processing modules
- __init__.py: Package initialization and main processing function
- extract_text.py: PDF text extraction
- generate_embeddings.py: Embedding generation using OpenAI
- store_embeddings.py: Embedding storage in ChromaDB
- docker-compose.yaml: Docker Compose configuration
- requirements.txt: Python dependencies

## Testing

To run tests (after implementing them):
docker-compose run app pytest

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]
This README provides an overview of the project, setup instructions, usage guide, and other relevant information. You can modify it as needed to better fit your project's specifics or add any additional sections you think would be helpful. CopyRetryOKThe API Key of openai is not needed as I am only using its library to generate embeddings EditI apologize for the misunderstanding. Thank you for clarifying that you're not using OpenAI's API for generating embeddings. Let's update the README and provide some recommendations based on this information.
Here's an updated version of the README, removing the OpenAI API key references:
markdownCopy# PDF Processing and Querying System

This project is a FastAPI-based application that processes PDF documents, extracts text, generates embeddings, and stores them in a vector database (ChromaDB) for efficient querying.

## Features

- PDF text extraction
- Text embedding generation
- Storage of embeddings in ChromaDB
- RESTful API for document upload and querying
- Containerized application using Docker

## Prerequisites

- Docker and Docker Compose

## Setup

1. Clone the repository:
git clone <repository-url>
cd <project-directory>

2. Build and run the Docker containers:
docker-compose up --build

## Usage

The application will be available at http://localhost:8080. You can use the following endpoints:

- POST /create_collection/{collection_name}: Create a new collection
- POST /add_documents/{collection_name}: Upload a PDF file to a collection
- GET /AllCollections: List all collections
- GET /query/{collection_name}: Query a collection
- DELETE /clear_database: Clear the database

Use a tool like curl or Postman to interact with the API.

## Project Structure

- api/: Main application directory
- main.py: FastAPI application
- uploaded_files/: Directory for uploaded PDFs
- pdf_processing/: PDF processing modules
- __init__.py: Package initialization and main processing function
- extract_text.py: PDF text extraction
- generate_embeddings.py: Embedding generation
- store_embeddings.py: Embedding storage in ChromaDB
- docker-compose.yaml: Docker Compose configuration
- requirements.txt: Python dependencies

## Testing

To run tests (after implementing them):
docker-compose run app pytest
Copy
## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License
