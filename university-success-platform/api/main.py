import os
from fastapi import FastAPI
import duckdb

app = FastAPI(
    title="Smart Platform for University Success - Prediction API",
    description="FastAPI service for serving student success prediction models.",
    version="1.0.0"
)

# Shared DuckDB database path inside container mount
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/university.duckdb")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Student Pass/Fail Prediction API",
        "database_configured_path": DATABASE_PATH
    }

@app.get("/health")
def health_check():
    # Check if the DuckDB file is accessible or if we can establish a connection
    try:
        # Create parent directory if it does not exist (SQLite/DuckDB standard)
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        conn = duckdb.connect(database=DATABASE_PATH, read_only=False)
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status
    }
