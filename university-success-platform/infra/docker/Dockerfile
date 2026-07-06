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
    dagster \
    dagster-webserver \
    duckdb \
    mlflow

# Copy the pipelines, ml, and other packages into the container
COPY pipelines/ /opt/dagster/app/pipelines/
COPY ml/ /opt/dagster/app/ml/

# Expose gRPC port 4000
EXPOSE 4000

# Start the Dagster gRPC server to serve user pipeline code to the Dagster webserver and daemon
CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-d", "/opt/dagster/app"]
