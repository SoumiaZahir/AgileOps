# data_quality/ — Livrable Imane Alouani (Data Quality Specialist)

Dispositif de contrôle qualité des données pour le projet **Smart Platform
for University Success**, basé sur **Great Expectations 1.18** et le dataset
OULAD. Couvre les **trois couches** du pipeline + la **cohérence inter-tables** :

- **Raw** — données brutes d'Aymen (`university.duckdb`, schéma `raw`)
- **Staging** — modèles dbt de Marouane (nettoyage `"?"`→NULL, cast, harmonisation)
- **Marts** — sortie dbt finale (`student_success_features`, `dim_courses`)
- **Cross-table** — contrôles d'intégrité référentielle entre tables

## Contenu

```
data_quality/
├── expectations/               # 16 Expectation Suites (7 raw + 7 staging + 2 marts)
├── checkpoints/                 # 7 Checkpoints raw
├── validation_definitions/      # 7 Validation Definitions raw
├── docs/
│   ├── data_quality_rules.md          # Documentation complète (3 couches + cross-table)
│   └── data_quality_reports/          # Data Docs HTML générés
│       └── index.html                 # <-- Point d'entrée à ouvrir
├── quality_issues_log.csv       # Journal horodaté des anomalies
├── scripts/
│   ├── 01_build_suites.py             # Suites RAW
│   ├── 02_build_checkpoints.py        # Checkpoints RAW
│   ├── 03_run_validation.py           # Validation RAW
│   ├── 04_build_marts_suites.py       # Suites MARTS
│   ├── 05_run_marts_validation.py     # Validation MARTS
│   ├── 06_build_staging_suites.py     # Suites STAGING
│   ├── 07_run_staging_validation.py   # Validation STAGING + cross-table
│   └── build_staging_tables.py        # Matérialise le staging depuis les modèles dbt
└── README.md
```

## Comment relancer la validation

Prérequis :
```bash
pip install great_expectations duckdb pandas
```

Placer `university.duckdb` (Aymen) à la racine et les CSV marts de Marouane
dans `data/marts/`, puis exécuter dans l'ordre :

```bash
# Couche RAW
python scripts/01_build_suites.py
python scripts/02_build_checkpoints.py
python scripts/03_run_validation.py

# Couche STAGING (matérialisation + validation + cross-table)
python scripts/build_staging_tables.py
python scripts/06_build_staging_suites.py
python scripts/07_run_staging_validation.py

# Couche MARTS
python scripts/04_build_marts_suites.py
python scripts/05_run_marts_validation.py --marts-dir data/marts
```

Le rapport HTML s'ouvre via `docs/data_quality_reports/index.html`.

## Note technique

La validation utilise le **moteur pandas** de Great Expectations (chaque table
chargée en DataFrame) plutôt qu'une connexion SQL directe à DuckDB, à cause
d'un bug connu `great_expectations==1.18` + `duckdb-engine` (calcul groupé de
métriques). Le contournement pandas est fiable pour ces tables (< 11M lignes).

La couche Staging est matérialisée en exécutant les modèles dbt de Marouane
(`build_staging_tables.py`) directement sur la base d'Aymen, en remplaçant la
macro `{{ source('raw', X) }}` par la référence réelle `raw.X`.

## Résultats (dernier run)

- **111 règles évaluées** : 41 raw + 34 staging + 4 cross-table + 32 marts
- **108 réussies**, **3 anomalies** (toutes en couche raw)
- **0 anomalie en Staging et Marts** ; **0 violation d'intégrité cross-table**
- Les anomalies raw (valeurs `"?"`) sont **neutralisées dès le staging** → la
  chaîne Raw → Staging → Marts est validée de bout en bout

Voir `docs/data_quality_rules.md` pour le détail complet et les recommandations.

## Intégration future avec Dagster (Maroua)

Chaque checkpoint raw s'appelle depuis un Asset/Op Dagster :
```python
import great_expectations as gx
context = gx.get_context(mode="file", project_root_dir=".")
result = context.checkpoints.get("student_info_checkpoint").run()
assert result.success, "Quality gate échoué avant la modélisation"
```
À placer comme étape obligatoire (quality gate) entre Transformation et
Modélisation dans le pipeline d'orchestration.
