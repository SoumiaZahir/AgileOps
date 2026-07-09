"""
Software-Defined Assets — Orchestration Dagster (Maroua)
=========================================================
Chaque asset représente une "table/étape" traçable du pipeline :

    raw_university_data  →  staging_models  →  marts_models  →  data_quality_checks
        (Aymen)                (Marouane)        (Marouane)          (Imane / dbt tests)

Les scripts d'Aymen et les modèles dbt de Marouane ne sont PAS réécrits :
ils sont simplement enveloppés (wrapped) comme assets pour que Dagster
gère l'ordre d'exécution, les retries et l'historique des runs.
"""

import os
import subprocess
import sys
from pathlib import Path

from dagster import (
    AssetExecutionContext,
    MetadataValue,
    RetryPolicy,
    asset,
)

# ---------------------------------------------------------------------------
# Résolution des chemins
# ---------------------------------------------------------------------------
# En local : la racine du repo est deux niveaux au-dessus de ce fichier.
# En conteneur (Docker de Soumia) : /opt/dagster/app — surchargable via env var.
REPO_ROOT = Path(os.getenv("DAGSTER_REPO_ROOT", Path(__file__).resolve().parents[2]))

INGESTION_DIR = REPO_ROOT / "pipelines" / "ingestion"
DBT_PROJECT_DIR = REPO_ROOT / "pipelines" / "transformation"
DBT_PROFILES_DIR = REPO_ROOT / "pipelines" / "orchestration" / "dbt_profiles"

# Politique de retry commune : 2 nouvelles tentatives, délai de 30 s
# (cf. docs/failure_handling.md pour la justification)
DEFAULT_RETRY_POLICY = RetryPolicy(max_retries=2, delay=30)


def _run_command(context: AssetExecutionContext, cmd: list[str], step_name: str) -> str:
    """Exécute une commande shell depuis la racine du repo et journalise la sortie."""
    context.log.info(f"[{step_name}] Commande : {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        context.log.info(result.stdout[-4000:])
    if result.returncode != 0:
        context.log.error(result.stderr[-4000:])
        raise RuntimeError(f"{step_name} a échoué (code {result.returncode})")
    return result.stdout


def _dbt(context: AssetExecutionContext, *args: str, step_name: str) -> str:
    """Lance une commande dbt avec le bon project-dir / profiles-dir."""
    cmd = [
        "dbt",
        *args,
        "--project-dir", str(DBT_PROJECT_DIR),
        "--profiles-dir", str(DBT_PROFILES_DIR),
    ]
    return _run_command(context, cmd, step_name)


# ---------------------------------------------------------------------------
# 1) RAW — ingestion (scripts d'Aymen)
# ---------------------------------------------------------------------------
@asset(
    compute_kind="python",
    group_name="ingestion",
    retry_policy=DEFAULT_RETRY_POLICY,
    description="Tables brutes OULAD chargées dans DuckDB (data/raw/university.duckdb) "
                "via les scripts d'ingestion d'Aymen (pipelines/ingestion/run_all.py).",
)
def raw_university_data(context: AssetExecutionContext) -> None:
    output = _run_command(
        context,
        [sys.executable, str(INGESTION_DIR / "run_all.py")],
        step_name="Ingestion (Aymen)",
    )
    # Un échec d'un script individuel est loggé par run_all mais ne fait pas
    # échouer le process → on le détecte explicitement ici.
    if "[ERREUR]" in output or "a échoué" in output:
        raise RuntimeError(
            "Au moins un script d'ingestion a échoué — voir data/raw/ingestion_log.jsonl"
        )
    n_ok = output.count("[OK]")
    context.add_output_metadata({
        "sources_ingérées": n_ok,
        "log": MetadataValue.path(str(REPO_ROOT / "data/raw/ingestion_log.jsonl")),
    })


# ---------------------------------------------------------------------------
# 2) STAGING — nettoyage initial (modèles dbt de Marouane)
# ---------------------------------------------------------------------------
@asset(
    deps=[raw_university_data],
    compute_kind="dbt",
    group_name="transformation",
    retry_policy=DEFAULT_RETRY_POLICY,
    description="Modèles dbt de la couche staging (nettoyage, typage, renommage) — Marouane.",
)
def staging_models(context: AssetExecutionContext) -> None:
    # Installe les packages dbt (dbt_utils) si absents — idempotent, donc
    # sans danger même déjà installés. Indispensable en conteneur neuf.
    _dbt(context, "deps", step_name="dbt deps")
    _dbt(context, "run", "--select", "staging", step_name="dbt staging")


# ---------------------------------------------------------------------------
# 3) MARTS — tables finales prêtes pour le ML et l'analytique
# ---------------------------------------------------------------------------
@asset(
    deps=[staging_models],
    compute_kind="dbt",
    group_name="transformation",
    retry_policy=DEFAULT_RETRY_POLICY,
    description="Modèles intermediate + marts, dont student_success_features "
                "(consommée par Abderahman/ML et Brahim/BI).",
)
def marts_models(context: AssetExecutionContext) -> None:
    _dbt(context, "run", "--select", "intermediate", "marts", step_name="dbt intermediate+marts")


# ---------------------------------------------------------------------------
# 4) QUALITY — contrôles de qualité (dbt tests + point d'intégration Imane)
# ---------------------------------------------------------------------------
@asset(
    deps=[marts_models],
    compute_kind="dbt",
    group_name="data_quality",
    retry_policy=RetryPolicy(max_retries=1, delay=15),
    description="Étape qualité OBLIGATOIRE : dbt tests (not_null, unique, relationships). "
                "Point d'intégration prévu pour les checkpoints Great Expectations d'Imane.",
)
def data_quality_checks(context: AssetExecutionContext) -> None:
    _dbt(context, "test", step_name="dbt tests (qualité)")

    # --- Point d'intégration Imane (Great Expectations) -------------------
    # Quand Imane livrera ses checkpoints, il suffira de dé-commenter :
    #
    # _run_command(
    #     context,
    #     ["great_expectations", "checkpoint", "run", "marts_checkpoint"],
    #     step_name="Great Expectations (Imane)",
    # )
    context.log.info("dbt tests OK — checkpoint Great Expectations d'Imane à brancher ici.")
