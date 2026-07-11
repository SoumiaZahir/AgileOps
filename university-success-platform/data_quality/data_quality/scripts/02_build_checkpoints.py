"""
02_build_checkpoints.py
------------------------
Cree un Checkpoint Great Expectations par table raw : associe une table a
son Expectation Suite, pret a etre declenche dans le pipeline (manuellement
ici, plus tard automatiquement par Maroua via Dagster).

A executer depuis data_quality/project/ :
    python scripts/02_build_checkpoints.py
"""

import great_expectations as gx
from great_expectations.exceptions.exceptions import DataContextError
from great_expectations.checkpoint import Checkpoint

DB_SCHEMA = "university.raw"

TABLES = {
    "courses": "courses_suite",
    "assessments": "assessments_suite",
    "student_info": "student_info_suite",
    "student_registration": "student_registration_suite",
    "student_assessment": "student_assessment_suite",
    "vle": "vle_suite",
    "student_vle": "student_vle_suite",
}


def get_or_add_table_asset(datasource, table_name):
    asset_name = f"{table_name}_asset"
    try:
        return datasource.get_asset(asset_name)
    except (KeyError, LookupError, DataContextError):
        return datasource.add_table_asset(
            name=asset_name, table_name=table_name, schema_name=DB_SCHEMA
        )


def get_or_add_batch_definition(asset, table_name):
    bd_name = f"{table_name}_whole_table"
    try:
        return asset.get_batch_definition(bd_name)
    except (KeyError, LookupError, DataContextError, ValueError):
        return asset.add_batch_definition_whole_table(bd_name)


def get_or_add_validation_definition(context, table_name, suite_name, batch_def):
    vd_name = f"{table_name}_validation"
    suite = context.suites.get(suite_name)
    try:
        return context.validation_definitions.get(vd_name)
    except (KeyError, LookupError, DataContextError):
        vd = gx.ValidationDefinition(name=vd_name, data=batch_def, suite=suite)
        return context.validation_definitions.add(vd)


def get_or_add_checkpoint(context, table_name, validation_definition):
    cp_name = f"{table_name}_checkpoint"
    try:
        return context.checkpoints.get(cp_name)
    except (KeyError, LookupError, DataContextError):
        checkpoint = Checkpoint(
            name=cp_name,
            validation_definitions=[validation_definition],
            result_format={"result_format": "SUMMARY"},
        )
        return context.checkpoints.add(checkpoint)


def main():
    context = gx.get_context(mode="file", project_root_dir=".")
    datasource = context.data_sources.get("university_db")

    print("Construction des Checkpoints (couche RAW)...\n")
    for table_name, suite_name in TABLES.items():
        asset = get_or_add_table_asset(datasource, table_name)
        batch_def = get_or_add_batch_definition(asset, table_name)
        validation_def = get_or_add_validation_definition(context, table_name, suite_name, batch_def)
        checkpoint = get_or_add_checkpoint(context, table_name, validation_def)
        print(f"  [OK] {checkpoint.name} pret (table: {table_name}, suite: {suite_name})")

    print("\nTous les checkpoints raw sont prets.")


if __name__ == "__main__":
    main()
