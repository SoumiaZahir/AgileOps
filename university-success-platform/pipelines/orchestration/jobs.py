"""
Jobs Dagster — Orchestration (Maroua)
======================================
Un job = une exécution complète et ordonnée du pipeline :

    Ingestion → Transformation (staging → marts) → Data Quality Checks

L'ordre est garanti par les dépendances déclarées entre les assets
(voir assets.py) : Dagster ne lance jamais la transformation avant
la fin de l'ingestion, ni les checks qualité avant les marts.
"""

from dagster import AssetSelection, define_asset_job

# Job principal : matérialise TOUS les assets dans l'ordre des dépendances.
university_success_pipeline = define_asset_job(
    name="university_success_pipeline",
    selection=AssetSelection.all(),
    description=(
        "Pipeline complet quotidien : ingestion OULAD (Aymen) → modèles dbt "
        "(Marouane) → contrôles qualité (dbt tests / Imane)."
    ),
    tags={"team": "data-engineering", "owner": "maroua"},
)

# Job partiel : uniquement la transformation + qualité (utile quand les
# données brutes n'ont pas changé mais que les modèles dbt ont été modifiés).
transformation_only_job = define_asset_job(
    name="transformation_only_job",
    selection=AssetSelection.groups("transformation", "data_quality"),
    description="Re-exécute uniquement dbt (staging → marts) + tests, sans ré-ingérer.",
    tags={"team": "data-engineering", "owner": "maroua"},
)
