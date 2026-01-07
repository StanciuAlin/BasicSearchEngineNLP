# Use the official Python 3.11-slim image as the base
# This provides a lightweight environment with Python pre-installed
FROM python:3.11-slim

# Set the working directory inside the container
# All subsequent commands and file copies will be relative to this path
WORKDIR /app

# Install system dependencies
# build-essential is required for compiling certain Python libraries (like those used in NLP)
# We clean up the apt cache to keep the image size small
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements.txt file first
# This is a Docker optimization: layers are cached, so dependencies are only 
# re-installed if requirements.txt changes, speeding up subsequent builds
COPY requirements.txt .

# Install Python dependencies specified in requirements.txt
# --no-cache-dir is used to further reduce the final image size
RUN pip install --no-cache-dir -r requirements.txt

# Download the spaCy English language model
# This model is required by the 'SpaCyStrategy' in the Preprocessing Factory
RUN python -m spacy download en_core_web_sm

# Optional: Download the Romanian language model if needed for future localized search
# RUN python -m spacy download ro_core_news_sm

# Copy the rest of the application source code into the container
# This includes the 'search_engine' logic, 'scripts', and data files
COPY . .

# Execute post-installation setup scripts
# 1. setup_nltk.py: Downloads necessary NLTK corpora (stopwords, punct, etc.) for the 'NLTKStrategy'
RUN python scripts/setup_nltk.py

# 2. fetch_library: Automatically populates the SQLite database (library.db) with 
# documents from Project Gutenberg to ensure the engine is ready for search on startup
RUN python -m scripts.fetch_library

# Expose port 8000 to allow external traffic to reach the FastAPI backend
EXPOSE 8000

# Command to launch the FastAPI application using the Uvicorn ASGI server
# --host 0.0.0.0 makes the server accessible from outside the container
# --port 8000 matches the exposed port
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]