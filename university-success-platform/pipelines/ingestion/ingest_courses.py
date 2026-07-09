"""
Ingestion des données de cours/modules (OULAD - courses.csv).
Usage : python ingest_courses.py
"""

import pandas as pd
from ingestion_utils import run_ingestion

SOURCE_PATH = "data/sources/courses.csv"


def load_courses():
    df = pd.read_csv(SOURCE_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


if __name__ == "__main__":
    run_ingestion(
        source_name="courses",
        table_name="courses",
        load_function=load_courses,
        original_source=SOURCE_PATH,
    )
