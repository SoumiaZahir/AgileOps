"""
Module utilitaire partagé pour tous les scripts d'ingestion.
Gère : connexion DuckDB, écriture des données, logging des runs, métadonnées.
"""

import duckdb
import json
import os
from datetime import datetime

DB_PATH = "data/raw/university.duckdb"
LOG_PATH = "data/raw/ingestion_log.jsonl"  # JSON Lines : 1 ligne = 1 run
METADATA_PATH = "data/raw/metadata.json"


def get_connection():
    """Ouvre (ou crée) la base DuckDB dans data/raw/."""
    os.makedirs("data/raw", exist_ok=True)
    return duckdb.connect(DB_PATH)


def load_dataframe_to_duckdb(df, table_name, schema="raw"):
    """
    Charge un DataFrame pandas dans une table DuckDB (remplace si elle existe).
    Retourne le nombre de lignes chargées.
    """
    con = get_connection()
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    con.register("df_temp", df)
    con.execute(f"CREATE OR REPLACE TABLE {schema}.{table_name} AS SELECT * FROM df_temp")
    row_count = con.execute(f"SELECT COUNT(*) FROM {schema}.{table_name}").fetchone()[0]
    con.close()
    return row_count


def log_ingestion_run(source_name, status, row_count=0, error_message=None, original_source=""):
    """
    Enregistre une entrée de log pour un run d'ingestion.
    Écrit en JSON Lines (append-only) dans data/raw/ingestion_log.jsonl
    """
    os.makedirs("data/raw", exist_ok=True)
    entry = {
        "source_name": source_name,
        "timestamp": datetime.now().isoformat(),
        "status": status,          # "success" ou "failed"
        "row_count": row_count,
        "error_message": error_message,
        "original_source": original_source,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def update_metadata(source_name, row_count, original_source):
    """
    Met à jour le fichier de métadonnées global (un enregistrement par source,
    écrasé à chaque run réussi avec les infos les plus récentes).
    """
    os.makedirs("data/raw", exist_ok=True)
    metadata = {}
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    metadata[source_name] = {
        "last_ingestion_date": datetime.now().isoformat(),
        "record_count": row_count,
        "original_source": original_source,
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def run_ingestion(source_name, table_name, load_function, original_source):
    """
    Wrapper générique qui exécute une ingestion, gère les erreurs,
    et log systématiquement le résultat (succès ou échec).

    load_function : fonction sans argument qui retourne un DataFrame pandas prêt à charger.
    """
    try:
        df = load_function()
        row_count = load_dataframe_to_duckdb(df, table_name)
        log_ingestion_run(source_name, "success", row_count=row_count, original_source=original_source)
        update_metadata(source_name, row_count, original_source)
        print(f"[OK] {source_name} : {row_count} lignes ingérées dans raw.{table_name}")
        return True
    except Exception as e:
        log_ingestion_run(source_name, "failed", error_message=str(e), original_source=original_source)
        print(f"[ERREUR] {source_name} : {e}")
        return False
