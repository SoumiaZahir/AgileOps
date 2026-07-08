# Transformation Layer — Lineage

Owner: Marouane. This is the dbt DAG for `pipelines/transformation/`.
The interactive, column-level version of this lineage graph is inside
`docs/dbt_docs/index.html` (open it locally, click "View Lineage Graph").

```mermaid
graph LR
  subgraph RAW["raw schema (Aymen's ingestion)"]
    R1[raw.courses]
    R2[raw.assessments]
    R3[raw.student_info]
    R4[raw.student_registration]
    R5[raw.student_assessment]
    R6[raw.vle]
    R7[raw.student_vle]
  end

  subgraph STAGING["staging (views, 1:1 cleaning)"]
    S1[stg_courses]
    S2[stg_assessments]
    S3[stg_student_info]
    S4[stg_student_registration]
    S5[stg_student_assessment]
    S6[stg_vle]
    S7[stg_student_vle]
  end

  subgraph INTERMEDIATE["intermediate (views, joins + aggregation)"]
    I1[int_student_assessment_joined]
    I2[int_student_assessment_agg]
    I3[int_student_vle_agg]
    I4[int_student_registration_clean]
  end

  subgraph MARTS["marts (tables, final)"]
    M1[dim_courses]
    M2[student_success_features]
  end

  R1 --> S1
  R2 --> S2
  R3 --> S3
  R4 --> S4
  R5 --> S5
  R6 --> S6
  R7 --> S7

  S5 --> I1
  S2 --> I1
  I1 --> I2
  S7 --> I3
  S4 --> I4

  S1 --> M1
  S3 --> M2
  M1 --> M2
  I2 --> M2
  I3 --> M2
  I4 --> M2
```

## Grain of each layer

| Layer | Grain | Materialization |
|---|---|---|
| staging | same as source (1 row per source row) | view |
| intermediate | mostly 1 row per student per presentation (except `int_student_assessment_joined`, which is 1 row per submission) | view |
| marts | 1 row per student per course presentation | table |

## Handoff

`marts.student_success_features` (also exported to `data/marts/student_success_features.csv`
and `.parquet`) is the contract with the rest of the team:

- **Abderahman** trains models on it (`ml/training/`).
- **Brahim** builds dashboards on it (`dashboards/`).
- **Imane** should point her Great Expectations suites at `staging` and `marts`
  schemas, not `raw` — raw is intentionally messy (that's Aymen's layer).
- **Maroua** wraps `dbt run` + `dbt test` as a Dagster op/asset that runs
  after ingestion and before quality checks/training.
