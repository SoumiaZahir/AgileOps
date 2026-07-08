"""
Ingestion des données des évaluations (OULAD - assessments.csv).
Usage : python ingest_assessments.py
"""

import pandas as pd
from ingestion_utils import run_ingestion

SOURCE_PATH = "data/sources/assessments.csv"


def load_assessments():
    df = pd.read_csv(SOURCE_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


if __name__ == "__main__":
    run_ingestion(
        source_name="assessments",
        table_name="assessments",
        load_function=load_assessments,
        original_source=SOURCE_PATH,
    )
