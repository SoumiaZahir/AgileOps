"""
Ingestion des scores des étudiants par évaluation
(OULAD - studentAssessment.csv). C'est l'équivalent des "notes".
Usage : python ingest_student_assessment.py
"""

import pandas as pd
from ingestion_utils import run_ingestion

SOURCE_PATH = "data/sources/studentAssessment.csv"


def load_student_assessment():
    df = pd.read_csv(SOURCE_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


if __name__ == "__main__":
    run_ingestion(
        source_name="student_assessment",
        table_name="student_assessment",
        load_function=load_student_assessment,
        original_source=SOURCE_PATH,
    )
