"""
Ingestion du catalogue des activités de la plateforme VLE
(OULAD - vle.csv).
Usage : python ingest_vle.py
"""

import pandas as pd
from ingestion_utils import run_ingestion

SOURCE_PATH = "data/sources/vle.csv"


def load_vle():
    df = pd.read_csv(SOURCE_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


if __name__ == "__main__":
    run_ingestion(
        source_name="vle",
        table_name="vle",
        load_function=load_vle,
        original_source=SOURCE_PATH,
    )
