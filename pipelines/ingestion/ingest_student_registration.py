"""
Ingestion des données d'inscription des étudiants
(OULAD - studentRegistration.csv).
Usage : python ingest_student_registration.py
"""

import pandas as pd
from ingestion_utils import run_ingestion

SOURCE_PATH = "data/sources/studentRegistration.csv"


def load_student_registration():
    df = pd.read_csv(SOURCE_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


if __name__ == "__main__":
    run_ingestion(
        source_name="student_registration",
        table_name="student_registration",
        load_function=load_student_registration,
        original_source=SOURCE_PATH,
    )
