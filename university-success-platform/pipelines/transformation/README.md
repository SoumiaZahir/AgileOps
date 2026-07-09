# Transformation Layer (Marouane — Data Engineer)

dbt project that turns Aymen's raw OULAD tables into a clean, modeling-ready
`student_success_features` table, following staging → intermediate → marts.

## Prerequisites
- Python 3.11+
- Aymen's `data/raw/university.duckdb` must exist (run his ingestion pipeline first:
  `pipelines/ingestion/run_all.py`).

## Setup
```bash
pip install -r requirements.txt
mkdir -p ~/.dbt
cp profiles.yml.example ~/.dbt/profiles.yml   # then edit the `path` if needed
dbt deps      # installs dbt-utils from GitHub (used for generic tests)
```

## Run
```bash
dbt run              # builds all staging/intermediate/marts models
dbt test              # runs all 38 data tests (not_null, unique, accepted_values, relationships)
dbt docs generate && dbt docs serve   # interactive docs + column-level lineage in your browser
```

## What gets built
| Schema | Materialization | Models |
|---|---|---|
| `staging` | view | `stg_courses`, `stg_assessments`, `stg_student_info`, `stg_student_registration`, `stg_student_assessment`, `stg_vle`, `stg_student_vle` |
| `intermediate` | view | `int_student_assessment_joined`, `int_student_assessment_agg`, `int_student_vle_agg`, `int_student_registration_clean` |
| `marts` | table | `dim_courses`, **`student_success_features`** (the final deliverable) |

See `docs/transformation_lineage.md` for the full DAG and
`docs/data_dictionary_student_success_features.md` for column-by-column
documentation of the final table.

## Notes for the team
- **Do not commit `*.duckdb` to git** — it's 65MB+ and will grow. It's in
  `.gitignore`. Each teammate regenerates it locally by running Aymen's
  ingestion script, or Soumia sets up shared storage per her infra role.
- `label_pass` embeds a business-rule assumption (Withdrawn = Fail). Flagged
  in the model SQL and the data dictionary — confirm with Aymen/Abderahman.
