# Multi-stage lightweight Python Dockerfile for AI-Powered Agriculture Crop Advisory Assistant
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies (build-essential for C extensions like faiss if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and assets
COPY app/ ./app/
COPY data/ ./data/
COPY frontend/ ./frontend/
COPY indexes/ ./indexes/
COPY models/ ./models/
COPY scripts/ ./scripts/
COPY docs/ ./docs/
COPY run.py .
COPY .env.example .env

# Expose FastAPI application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application server
CMD ["python", "run.py"]
