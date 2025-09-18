# Dockerfile for Climate Assistant RAG System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/documents data/vector_store data/evaluation

# Set environment variables
ENV PYTHONPATH=/app
ENV OLLAMA_BASE_URL=http://localhost:11434
ENV LLM_MODEL=llama3.1:8b
ENV VECTOR_STORE_TYPE=faiss
ENV API_HOST=0.0.0.0
ENV API_PORT=5000

# Expose port
EXPOSE 5000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Ollama service..."\n\
ollama serve &\n\
sleep 5\n\
echo "Pulling LLM model..."\n\
ollama pull llama3.1:8b\n\
echo "Processing documents..."\n\
python -m ingest.document_processor\n\
echo "Starting API server..."\n\
python -m app.app' > start.sh && chmod +x start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start the application
CMD ["./start.sh"]
