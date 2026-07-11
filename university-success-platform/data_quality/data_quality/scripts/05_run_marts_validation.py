"""
05_run_marts_validation.py
----------------------------
Valide les tables de la couche MARTS (sortie dbt de Marouane) contre leurs
Expectation Suites, et met a jour :
  - docs/data_quality_reports/  (Data Docs HTML, tous runs confondus)
  - quality_issues_log.csv       (journal des anomalies, en mode append)

Les CSV marts sont lus depuis MARTS_DIR (par defaut : data/marts/).

A executer depuis data_quality/project/ :
    python scripts/05_run_marts_validation.py --marts-dir /chemin/vers/data/marts
"""

import argparse
import csv
import datetime as dt
import os

import pandas as pd
import great_expectations as gx
from great_expectations.exceptions.exceptions import DataContextError

LOG_PATH = "quality_issues_log.csv"

# fichier csv -> (nom de suite, nom logique de table)
MARTS = {
    "student_success_features.csv": ("marts_student_success_features_suite", "marts_student_success_features"),
    "dim_courses.csv": ("marts_dim_courses_suite", "marts_dim_courses"),
}


def get_or_add_pandas_datasource(context):
    try:
        return context.data_sources.get("pandas_ds")
    except (KeyError, LookupError, DataContextError):
        return context.data_sources.add_pandas(name="pandas_ds")


def get_or_add_dataframe_asset(datasource, table_name):
    asset_name = f"{table_name}_df"
    try:
        return datasource.get_asset(asset_name)
    except (KeyError, LookupError, DataContextError):
        return datasource.add_dataframe_asset(name=asset_name)


def get_or_add_batch_definition(asset, table_name):
    bd_name = f"{table_name}_bd"
    try:
        return asset.get_batch_definition(bd_name)
    except (KeyError, LookupError, DataContextError, ValueError):
        return asset.add_batch_definition_whole_dataframe(bd_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--marts-dir", default="data/marts", help="Dossier des CSV marts")
    args = parser.parse_args()

    context = gx.get_context(mode="file", project_root_dir=".")
    pandas_ds = get_or_add_pandas_datasource(context)

    rows = []
    now = dt.datetime.now().isoformat(timespec="seconds")

    print("Validation de la couche MARTS...\n")
    for csv_name, (suite_name, table_name) in MARTS.items():
        path = os.path.join(args.marts_dir, csv_name)
        if not os.path.exists(path):
            print(f"  [SKIP] {csv_name} introuvable dans {args.marts_dir}")
            continue

        df = pd.read_csv(path)
        asset = get_or_add_dataframe_asset(pandas_ds, table_name)
        batch_def = get_or_add_batch_definition(asset, table_name)
        batch = batch_def.get_batch(batch_parameters={"dataframe": df})

        suite = context.suites.get(suite_name)
        result = batch.validate(suite)

        for exp_result in result.results:
            exp_type = exp_result.expectation_config.type
            column = exp_result.expectation_config.kwargs.get("column", "")
            exp_success = exp_result.success
            unexpected_count = (exp_result.result or {}).get("unexpected_count", 0)
            status = "resolved" if exp_success else "pending"
            rows.append(
                {
                    "date_check": now,
                    "table": table_name,
                    "rule": exp_type,
                    "column": column,
                    "success": exp_success,
                    "unexpected_count": unexpected_count,
                    "status": status,
                }
            )

        status_label = "SUCCES" if result.success else "ANOMALIES DETECTEES"
        n_fail = sum(1 for r in result.results if not r.success)
        print(f"  [{status_label}] {table_name}  ({n_fail}/{len(result.results)} regles en echec)")

    # Append au log existant (on garde l'historique du run raw)
    file_exists = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date_check", "table", "rule", "column",
                "success", "unexpected_count", "status",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    n_pending = sum(1 for r in rows if r["status"] == "pending")
    print(f"\nLog mis a jour : {LOG_PATH} (+{len(rows)} regles marts, {n_pending} en attente)")

    context.build_data_docs()
    print("Data Docs regeneres.")


if __name__ == "__main__":
    main()
