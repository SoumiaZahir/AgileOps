# Politique de gestion des échecs — Retry & Alerting (Maroua)

> Livrable : Data Engineer (Orchestration) — coordonné avec Hanane (Monitoring)

## 1. Politique de retry (nouvelle tentative automatique)

| Asset | Max retries | Délai | Justification |
|---|---|---|---|
| `raw_university_data` | 2 | 30 s | Les échecs d'ingestion sont souvent transitoires (fichier en cours de copie, verrou DuckDB) |
| `staging_models` | 2 | 30 s | Verrou de fichier DuckDB possible si un autre process lit la base |
| `marts_models` | 2 | 30 s | Idem staging |
| `data_quality_checks` | 1 | 15 s | Un test qualité qui échoue est presque toujours un **vrai problème de données** — inutile de réessayer 2 fois |

Implémentation : `RetryPolicy(max_retries=..., delay=...)` sur chaque asset (`assets.py`).

**Comportement vérifié en test** : lors d'un échec dbt volontaire, Dagster a bien relancé
l'étape 2 fois (`STEP_UP_FOR_RETRY` → `STEP_RESTARTED`) avant de marquer `STEP_FAILURE`,
et les assets aval ont été annulés.

## 2. Concurrence

`max_concurrent_runs: 1` (dagster.yaml) : le pipeline écrit dans **un seul fichier DuckDB** ;
deux runs simultanés provoqueraient des conflits de verrou. Un run déclenché pendant qu'un
autre tourne est mis en file d'attente, jamais perdu.

## 3. Alerting en cas d'échec

Le sensor `pipeline_failure_alert` (`schedules.py`) s'exécute à chaque **échec de run** :

1. **Log structuré** dans le daemon Dagster (toujours actif) : nom du job, run ID, message d'erreur.
2. **Webhook Slack** (canal de Hanane) : si la variable d'environnement `SLACK_WEBHOOK_URL`
   est définie (par Soumia dans docker-compose / GitHub Secrets), un message formaté est envoyé :

   ```
   🚨 ÉCHEC pipeline Dagster
   • Job : university_success_pipeline
   • Run ID : xxxx-xxxx
   • Erreur : <message>
   ```
3. L'envoi Slack est **fail-safe** : une erreur réseau du webhook est loggée mais ne fait
   jamais planter le daemon.

### Intégration avec le monitoring de Hanane

- Les échecs de pipeline arrivent dans le **même canal Slack** que les alertes Grafana.
- Point d'extension prévu : remplacer le webhook direct par un push vers l'Alertmanager
  de Prometheus si Hanane préfère centraliser.

## 4. Diagnostic d'un échec — procédure

1. Ouvrir **Dagit → Runs** : le run en échec est en rouge, cliquer dessus.
2. Onglet **Logs** : l'asset fautif affiche la sortie complète de la commande
   (stdout/stderr d'ingestion ou de dbt, tronquée à 4000 caractères).
3. Cas fréquents :
   - Ingestion : consulter `data/raw/ingestion_log.jsonl` (log JSON Lines d'Aymen).
   - dbt : relancer manuellement `dbt run --select <modele> --project-dir pipelines/transformation --profiles-dir pipelines/orchestration/dbt_profiles` pour reproduire.
   - Qualité : les tests dbt en échec listent la table/colonne exacte.
4. Après correction, relancer uniquement les assets en aval via Dagit (*Materialize* sur
   l'asset corrigé — Dagster propage automatiquement).
