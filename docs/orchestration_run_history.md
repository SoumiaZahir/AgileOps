# Historique des runs — Tests d'orchestration (Maroua)

> Runs exécutés lors de la validation du pipeline dans un environnement équivalent
> au conteneur `dagster_workspace` (Python 3.12, dagster 1.13, dbt-duckdb 1.10,
> données synthétiques fidèles au format OULAD : mêmes colonnes, mêmes valeurs `'?'`).
> En production, cet historique est visible en direct dans **Dagit → Runs**.

| # | Run | Statut | Détail |
|---|---|---|---|
| 1 | Chargement des Definitions | ✅ SUCCÈS | 4 assets, 2 jobs, 1 schedule, 2 sensors détectés |
| 2 | Run complet (1ʳᵉ tentative) | ❌ ÉCHEC (attendu) | `dbt deps` manquant → **retry policy validée** : 2 relances automatiques (`STEP_UP_FOR_RETRY`) puis échec propre, assets aval annulés |
| 3 | Run complet (après fix `dbt deps` auto) | ❌ ÉCHEC | Données de test trop "propres" (colonnes numériques sans `'?'`) — pas un bug du pipeline |
| 4 | Run complet (données OULAD-fidèles) | ✅ SUCCÈS | Ingestion 7/7 → staging 7/7 → marts 6/6 → **38 tests dbt PASS** |
| 5 | Test sensor (1ᵉʳ passage) | ✅ SUCCÈS | `RunRequest` émis (nouveaux fichiers détectés) |
| 6 | Test sensor (2ᵉ passage, rien de nouveau) | ✅ SUCCÈS | `SkipReason` — pas de run inutile (curseur anti-doublon OK) |
| 7 | Run complet n°2 | ✅ SUCCÈS | 23.4 s |
| 8 | Run complet n°3 | ✅ SUCCÈS | 24.9 s |
| 9 | Run complet n°4 | ✅ SUCCÈS | 21.3 s |
| 10 | Vérification table finale | ✅ SUCCÈS | `marts.student_success_features` : 300 lignes × 26 colonnes |

## Enseignements des échecs (runs 2-3)

- **Run 2** a prouvé que la `RetryPolicy` et l'annulation des assets aval fonctionnent
  exactement comme spécifié dans `docs/failure_handling.md`.
- **Correctif durable** : l'asset `staging_models` exécute désormais `dbt deps`
  automatiquement (idempotent) — indispensable pour un conteneur Docker fraîchement
  construit, qui n'a jamais installé `dbt_utils`.

## À refaire avec les vraies données

Les CSV OULAD réels (`data/sources/`) étant gitignorés, chaque membre doit les placer
localement puis lancer :

```bash
dagster dev -w pipelines/orchestration/workspace.yaml
# puis dans Dagit (http://localhost:3000) → Assets → Materialize all
```
