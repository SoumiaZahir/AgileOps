# Use Python 3.11 slim image for a lightweight, production-ready environment
FROM python:3.11-slim

# Set environment variables to optimize Python performance inside the container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install FastAPI, Uvicorn, DuckDB and MLflow dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    duckdb \
    mlflow

# Copy the API implementation files to the app directory
COPY . /app

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Start the uvicorn server to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
