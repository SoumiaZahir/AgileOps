"""
Schedules & Sensors — Orchestration (Maroua)
=============================================
1. daily_pipeline_schedule : exécution quotidienne planifiée (cron 02:00).
2. new_source_file_sensor  : déclenche le pipeline dès qu'un fichier CSV
   source est ajouté/modifié dans data/sources/ (trigger "à l'arrivée").
3. pipeline_failure_alert  : alerte en cas d'échec de run — log + webhook
   Slack (canal fourni par Hanane via la variable d'env SLACK_WEBHOOK_URL).
"""

import json
import os
import urllib.request
from pathlib import Path

from dagster import (
    DefaultScheduleStatus,
    DefaultSensorStatus,
    RunFailureSensorContext,
    RunRequest,
    ScheduleDefinition,
    SensorEvaluationContext,
    SkipReason,
    run_failure_sensor,
    sensor,
)

from .assets import REPO_ROOT
from .jobs import university_success_pipeline

SOURCES_DIR = REPO_ROOT / "data" / "sources"

# ---------------------------------------------------------------------------
# 1) Schedule quotidien — tous les jours à 02h00 (heure de Casablanca)
# ---------------------------------------------------------------------------
daily_pipeline_schedule = ScheduleDefinition(
    name="daily_pipeline_schedule",
    job=university_success_pipeline,
    cron_schedule="0 2 * * *",
    execution_timezone="Africa/Casablanca",
    default_status=DefaultScheduleStatus.RUNNING,
)


# ---------------------------------------------------------------------------
# 2) Sensor "nouveau fichier" — surveille data/sources/ toutes les 60 s
# ---------------------------------------------------------------------------
@sensor(
    name="new_source_file_sensor",
    job=university_success_pipeline,
    minimum_interval_seconds=60,
    default_status=DefaultSensorStatus.RUNNING,
    description="Déclenche le pipeline complet quand un CSV source apparaît ou change.",
)
def new_source_file_sensor(context: SensorEvaluationContext):
    if not SOURCES_DIR.exists():
        return SkipReason(f"Dossier introuvable : {SOURCES_DIR}")

    # Empreinte = nom + date de modification de chaque CSV
    fingerprint = {
        f.name: f.stat().st_mtime for f in sorted(SOURCES_DIR.glob("*.csv"))
    }
    if not fingerprint:
        return SkipReason("Aucun fichier CSV dans data/sources/")

    current_state = json.dumps(fingerprint, sort_keys=True)
    if context.cursor == current_state:
        return SkipReason("Aucun nouveau fichier ni modification détectés.")

    context.update_cursor(current_state)
    newest = max(fingerprint, key=fingerprint.get)
    return RunRequest(
        run_key=current_state[:64] + newest,  # évite les doublons de runs
        tags={"trigger": "new_file", "fichier_declencheur": newest},
    )


# ---------------------------------------------------------------------------
# 3) Alerting en cas d'échec — coordonné avec Hanane (Monitoring)
# ---------------------------------------------------------------------------
@run_failure_sensor(
    name="pipeline_failure_alert",
    default_status=DefaultSensorStatus.RUNNING,
    description="Envoie une alerte (log + Slack webhook de Hanane) quand un run échoue.",
)
def pipeline_failure_alert(context: RunFailureSensorContext):
    message = (
        f":rotating_light: ÉCHEC pipeline Dagster\n"
        f"• Job : {context.dagster_run.job_name}\n"
        f"• Run ID : {context.dagster_run.run_id}\n"
        f"• Erreur : {context.failure_event.message}"
    )
    context.log.error(message)

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")  # fourni par Hanane
    if not webhook_url:
        context.log.warning(
            "SLACK_WEBHOOK_URL non définie — alerte loggée uniquement. "
            "Voir docs/failure_handling.md."
        )
        return

    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps({"text": message}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        context.log.info("Alerte Slack envoyée.")
    except Exception as exc:  # l'alerting ne doit jamais casser le daemon
        context.log.error(f"Échec de l'envoi Slack : {exc}")
