# Schéma des données brutes (raw) — Dataset OULAD

> Généré automatiquement à partir des VRAIES données uploadées, base DuckDB `data/raw/university.duckdb`

## Table : `raw.assessments`

| Colonne | Type | Nullable |
|---|---|---|
| code_module | VARCHAR | YES |
| code_presentation | VARCHAR | YES |
| id_assessment | BIGINT | YES |
| assessment_type | VARCHAR | YES |
| date | DOUBLE | YES |
| weight | DOUBLE | YES |

**Nombre de lignes (données réelles) :** 206

---

## Table : `raw.courses`

| Colonne | Type | Nullable |
|---|---|---|
| code_module | VARCHAR | YES |
| code_presentation | VARCHAR | YES |
| module_presentation_length | BIGINT | YES |

**Nombre de lignes (données réelles) :** 22

---

## Table : `raw.student_assessment`

| Colonne | Type | Nullable |
|---|---|---|
| id_assessment | BIGINT | YES |
| id_student | BIGINT | YES |
| date_submitted | BIGINT | YES |
| is_banked | BIGINT | YES |
| score | DOUBLE | YES |

**Nombre de lignes (données réelles) :** 173,912

---

## Table : `raw.student_info`

| Colonne | Type | Nullable |
|---|---|---|
| code_module | VARCHAR | YES |
| code_presentation | VARCHAR | YES |
| id_student | BIGINT | YES |
| gender | VARCHAR | YES |
| region | VARCHAR | YES |
| highest_education | VARCHAR | YES |
| imd_band | VARCHAR | YES |
| age_band | VARCHAR | YES |
| num_of_prev_attempts | BIGINT | YES |
| studied_credits | BIGINT | YES |
| disability | VARCHAR | YES |
| final_result | VARCHAR | YES |

**Nombre de lignes (données réelles) :** 32,593

---

## Table : `raw.student_registration`

| Colonne | Type | Nullable |
|---|---|---|
| code_module | VARCHAR | YES |
| code_presentation | VARCHAR | YES |
| id_student | BIGINT | YES |
| date_registration | DOUBLE | YES |
| date_unregistration | DOUBLE | YES |

**Nombre de lignes (données réelles) :** 32,593

---

## Table : `raw.student_vle`

| Colonne | Type | Nullable |
|---|---|---|
| code_module | VARCHAR | YES |
| code_presentation | VARCHAR | YES |
| id_student | BIGINT | YES |
| id_site | BIGINT | YES |
| date | BIGINT | YES |
| sum_click | BIGINT | YES |

**Nombre de lignes (données réelles) :** 10,655,280

---

## Table : `raw.vle`

| Colonne | Type | Nullable |
|---|---|---|
| id_site | BIGINT | YES |
| code_module | VARCHAR | YES |
| code_presentation | VARCHAR | YES |
| activity_type | VARCHAR | YES |
| week_from | DOUBLE | YES |
| week_to | DOUBLE | YES |

**Nombre de lignes (données réelles) :** 6,364

---

