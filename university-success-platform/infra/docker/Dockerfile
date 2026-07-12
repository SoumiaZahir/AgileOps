# Use Python 3.11 slim image for a lightweight, production-ready environment
FROM python:3.11-slim

# Set workspace environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DAGSTER_HOME=/opt/dagster/dagster_home

# Set working directory inside the container
WORKDIR /opt/dagster/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Dagster and data engineering dependencies
RUN pip install --no-cache-dir \
    --default-timeout=120 \
    --retries=10 \
    dagster \
    dagster-webserver \
    duckdb \
    mlflow

# Installez également les dépendances de votre projet
COPY pipelines/orchestration/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the pipelines, ml, and other packages into the container
COPY pipelines/ /opt/dagster/app/pipelines/
COPY ml/ /opt/dagster/app/ml/

# Expose gRPC port 4000
EXPOSE 4000

# CONFIGURATION FINALE : On se place dans le dossier parent 'pipelines'
WORKDIR /opt/dagster/app/pipelines

# On lance orchestration.definitions pour trouver l'objet Definitions
CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-m", "orchestration.definitions"]
