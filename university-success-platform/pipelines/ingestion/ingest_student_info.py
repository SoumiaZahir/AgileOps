"""
Ingestion des informations démographiques et résultats des étudiants
(OULAD - studentInfo.csv).
Usage : python ingest_student_info.py
"""

import pandas as pd
from ingestion_utils import run_ingestion

SOURCE_PATH = "data/sources/studentInfo.csv"


def load_student_info():
    df = pd.read_csv(SOURCE_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


if __name__ == "__main__":
    run_ingestion(
        source_name="student_info",
        table_name="student_info",
        load_function=load_student_info,
        original_source=SOURCE_PATH,
    )
