"""
03_run_validation.py
----------------------
Charge chaque table raw depuis university.duckdb, la valide contre sa suite
Great Expectations (moteur pandas), et genere :
  - docs/data_quality_reports/  (Data Docs HTML)
  - quality_issues_log.csv       (journal des anomalies, ecrase a chaque run raw)

NOTE TECHNIQUE : on utilise le moteur pandas de Great Expectations plutot
que la connexion SQL directe a DuckDB. La combinaison GX 1.18 +
duckdb-engine presente un bug connu de calcul groupe de metrics
("bundled metrics" -> IndexError cote SQLAlchemy). Charger la table en
DataFrame avant validation contourne le probleme et reste performant pour
des tables de cette taille (< 11M lignes).

A executer depuis data_quality/project/ :
    python scripts/03_run_validation.py
"""

import csv
import datetime as dt

import duckdb
import great_expectations as gx
from great_expectations.exceptions.exceptions import DataContextError

DB_PATH = "university.duckdb"
SCHEMA = "raw"
LOG_PATH = "quality_issues_log.csv"

TABLES = [
    "courses", "assessments", "student_info", "student_registration",
    "student_assessment", "vle", "student_vle",
]


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
    context = gx.get_context(mode="file", project_root_dir=".")
    pandas_ds = get_or_add_pandas_datasource(context)
    con = duckdb.connect(DB_PATH, read_only=True)

    rows = []
    now = dt.datetime.now().isoformat(timespec="seconds")

    print("Validation des tables (couche RAW)...\n")
    for table_name in TABLES:
        df = con.execute(f"SELECT * FROM {SCHEMA}.{table_name}").fetchdf()
        asset = get_or_add_dataframe_asset(pandas_ds, table_name)
        batch_def = get_or_add_batch_definition(asset, table_name)
        batch = batch_def.get_batch(batch_parameters={"dataframe": df})
        suite = context.suites.get(f"{table_name}_suite")
        result = batch.validate(suite)

        for exp_result in result.results:
            rows.append({
                "date_check": now,
                "table": table_name,
                "rule": exp_result.expectation_config.type,
                "column": exp_result.expectation_config.kwargs.get("column", ""),
                "success": exp_result.success,
                "unexpected_count": (exp_result.result or {}).get("unexpected_count", 0),
                "status": "resolved" if exp_result.success else "pending",
            })

        status_label = "SUCCES" if result.success else "ANOMALIES DETECTEES"
        n_fail = sum(1 for r in result.results if not r.success)
        print(f"  [{status_label}] {table_name}  ({n_fail}/{len(result.results)} regles en echec)")

    con.close()

    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "date_check", "table", "rule", "column", "success", "unexpected_count", "status",
        ])
        writer.writeheader()
        writer.writerows(rows)

    n_pending = sum(1 for r in rows if r["status"] == "pending")
    print(f"\nLog ecrit : {LOG_PATH} ({len(rows)} regles evaluees, {n_pending} en attente)")

    context.build_data_docs()
    print("Data Docs generes dans gx/uncommitted/data_docs/local_site/")


if __name__ == "__main__":
    main()
