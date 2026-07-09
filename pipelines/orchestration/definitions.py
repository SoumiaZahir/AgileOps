"""
Point d'entrée Dagster — Definitions (Maroua)
==============================================
Regroupe assets + jobs + schedules + sensors en un seul objet `defs`
chargé par le webserver/daemon Dagster (voir workspace.yaml de Soumia).
"""

from dagster import Definitions, load_assets_from_modules

from . import assets
from .jobs import transformation_only_job, university_success_pipeline
from .schedules import (
    daily_pipeline_schedule,
    new_source_file_sensor,
    pipeline_failure_alert,
)

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    jobs=[university_success_pipeline, transformation_only_job],
    schedules=[daily_pipeline_schedule],
    sensors=[new_source_file_sensor, pipeline_failure_alert],
)
