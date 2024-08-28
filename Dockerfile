# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p pdf db_pdf db_scrape

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# The CMD is specified in docker-compose.yml