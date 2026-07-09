"""
Ingestion des logs d'interactions étudiants sur la plateforme VLE
(OULAD - studentVle.csv). C'est l'équivalent de l'engagement/"présence".

ATTENTION : ce fichier est volumineux (~44 Mo compressé, ~443 Mo décompressé
selon ta capture). Ce script lit par chunks pour éviter de saturer la RAM.

Usage : python ingest_student_vle.py
"""

import pandas as pd
from ingestion_utils import get_connection, log_ingestion_run, update_metadata

SOURCE_PATH = "data/sources/studentVle.csv"
CHUNK_SIZE = 200_000  # ajuste selon la RAM disponible


def ingest_student_vle_chunked():
    con = get_connection()
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    total_rows = 0
    first_chunk = True

    try:
        for chunk in pd.read_csv(SOURCE_PATH, chunksize=CHUNK_SIZE):
            chunk.columns = [c.strip().lower() for c in chunk.columns]
            con.register("chunk_temp", chunk)

            if first_chunk:
                con.execute("CREATE OR REPLACE TABLE raw.student_vle AS SELECT * FROM chunk_temp")
                first_chunk = False
            else:
                con.execute("INSERT INTO raw.student_vle SELECT * FROM chunk_temp")

            total_rows += len(chunk)
            print(f"  ... {total_rows} lignes chargées jusqu'ici")

        con.close()
        log_ingestion_run("student_vle", "success", row_count=total_rows, original_source=SOURCE_PATH)
        update_metadata("student_vle", total_rows, SOURCE_PATH)
        print(f"[OK] student_vle : {total_rows} lignes ingérées dans raw.student_vle")
        return True

    except Exception as e:
        con.close()
        log_ingestion_run("student_vle", "failed", error_message=str(e), original_source=SOURCE_PATH)
        print(f"[ERREUR] student_vle : {e}")
        return False


if __name__ == "__main__":
    ingest_student_vle_chunked()
