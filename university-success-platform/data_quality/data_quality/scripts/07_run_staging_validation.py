"""
07_run_staging_validation.py
------------------------------
Valide la couche STAGING (materialisee par build_staging_tables.py) contre
ses Expectation Suites, PLUS des controles de coherence CROSS-TABLE
(integrite referentielle entre tables), comme demande dans le cahier des
charges ("cross-table consistency").

Met a jour :
  - docs/data_quality_reports/  (Data Docs HTML)
  - quality_issues_log.csv       (append)

A executer depuis data_quality/project/ (apres 06_build_staging_suites.py) :
    python scripts/07_run_staging_validation.py
"""

import csv
import datetime as dt

import duckdb
import great_expectations as gx
from great_expectations.exceptions.exceptions import DataContextError

STAGING_DB = "staging_tables.duckdb"
SCHEMA = "staging"
LOG_PATH = "quality_issues_log.csv"

# table staging -> suite
TABLES = {
    "stg_courses": "staging_stg_courses_suite",
    "stg_assessments": "staging_stg_assessments_suite",
    "stg_student_info": "staging_stg_student_info_suite",
    "stg_student_registration": "staging_stg_student_registration_suite",
    "stg_student_assessment": "staging_stg_student_assessment_suite",
    "stg_vle": "staging_stg_vle_suite",
    "stg_student_vle": "staging_stg_student_vle_suite",
}

# Controles de coherence cross-table (integrite referentielle) :
# (nom, requete SQL renvoyant le nombre de lignes ORPHELINES = violations)
CROSS_TABLE_CHECKS = [
    (
        "student_assessment.id_assessment existe dans assessments",
        """SELECT COUNT(*) FROM staging.stg_student_assessment sa
           LEFT JOIN staging.stg_assessments a USING(id_assessment)
           WHERE a.id_assessment IS NULL""",
    ),
    (
        "student_info.id_student a une inscription (student_registration)",
        """SELECT COUNT(*) FROM staging.stg_student_info si
           LEFT JOIN staging.stg_student_registration sr
             ON si.student_presentation_id = sr.student_presentation_id
           WHERE sr.student_presentation_id IS NULL""",
    ),
    (
        "assessments.(code_module,code_presentation) existe dans courses",
        """SELECT COUNT(*) FROM staging.stg_assessments a
           LEFT JOIN staging.stg_courses c
             ON a.code_module = c.code_module
            AND a.code_presentation = c.code_presentation
           WHERE c.code_module IS NULL""",
    ),
    (
        "vle.(code_module,code_presentation) existe dans courses",
        """SELECT COUNT(*) FROM staging.stg_vle v
           LEFT JOIN staging.stg_courses c
             ON v.code_module = c.code_module
            AND v.code_presentation = c.code_presentation
           WHERE c.code_module IS NULL""",
    ),
]


def get_or_add_pandas_datasource(context):
    try:
        return context.data_sources.get("pandas_ds")
    except (KeyError, LookupError, DataContextError):
        return context.data_sources.add_pandas(name="pandas_ds")


def get_or_add_dataframe_asset(datasource, table_name):
    try:
        return datasource.get_asset(f"{table_name}_df")
    except (KeyError, LookupError, DataContextError):
        return datasource.add_dataframe_asset(name=f"{table_name}_df")


def get_or_add_batch_definition(asset, table_name):
    try:
        return asset.get_batch_definition(f"{table_name}_bd")
    except (KeyError, LookupError, DataContextError, ValueError):
        return asset.add_batch_definition_whole_dataframe(f"{table_name}_bd")


def main():
    context = gx.get_context(mode="file", project_root_dir=".")
    pandas_ds = get_or_add_pandas_datasource(context)
    con = duckdb.connect(STAGING_DB, read_only=True)

    rows = []
    now = dt.datetime.now().isoformat(timespec="seconds")

    print("Validation de la couche STAGING...\n")
    for table_name, suite_name in TABLES.items():
        df = con.execute(f"SELECT * FROM {SCHEMA}.{table_name}").fetchdf()
        asset = get_or_add_dataframe_asset(pandas_ds, table_name)
        batch_def = get_or_add_batch_definition(asset, table_name)
        batch = batch_def.get_batch(batch_parameters={"dataframe": df})
        suite = context.suites.get(suite_name)
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

    # --- Controles cross-table ---
    print("\nControles de coherence CROSS-TABLE...\n")
    for check_name, sql in CROSS_TABLE_CHECKS:
        violations = con.execute(sql).fetchone()[0]
        success = violations == 0
        rows.append({
            "date_check": now,
            "table": "cross_table",
            "rule": "referential_integrity",
            "column": check_name,
            "success": success,
            "unexpected_count": violations,
            "status": "resolved" if success else "pending",
        })
        label = "OK" if success else f"VIOLATIONS: {violations}"
        print(f"  [{label}] {check_name}")

    con.close()

    # Append au log
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "date_check", "table", "rule", "column", "success", "unexpected_count", "status",
        ])
        writer.writerows(rows)

    n_pending = sum(1 for r in rows if r["status"] == "pending")
    print(f"\nLog mis a jour : {LOG_PATH} (+{len(rows)} regles staging + cross-table, {n_pending} en attente)")

    context.build_data_docs()
    print("Data Docs regeneres.")


if __name__ == "__main__":
    main()
