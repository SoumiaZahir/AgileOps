# Data Ingestion Pipeline

## Description

This project implements the raw data ingestion pipeline for the OULAD dataset.

The pipeline:

- Reads raw CSV files
- Loads data into DuckDB
- Generates ingestion logs
- Updates ingestion metadata

## Project Structure

```
DATA_INGESTION/
│
├── data/
│   ├── sources/
│   └── raw/
│
├── docs/
│
├── pipelines/
│   └── ingestion/
```

## Requirements

- Python 3.13+
- pandas
- duckdb

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run the pipeline

```bash
python pipelines/ingestion/run_all.py
```

## Output

The pipeline creates:

- data/raw/university.duckdb
- data/raw/metadata.json
- data/raw/ingestion_log.jsonl
## Dataset

The dataset is stored on Google Drive because some files exceed GitHub's size limit.

Download the dataset from:

https://drive.google.com/drive/folders/1v6GwNzzAiyG5FJPWtSeCYtMMamGrz9bu

Extract the files and place them in:

data/sources/

Then run:

```bash
python pipelines/ingestion/run_all.py
```