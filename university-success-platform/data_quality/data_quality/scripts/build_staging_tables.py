"""
build_staging_tables.py
-------------------------
Materialise la couche STAGING de Marouane en executant ses modeles dbt
directement sur la base DuckDB d'Aymen. On remplace la macro dbt
{{ source('raw', 'X') }} par la reference reelle raw.X.

Produit un fichier staging_tables.duckdb contenant le schema `staging`.
"""

import duckdb
import re

SRC_DB = "university.duckdb"          # base d'Aymen (raw)
OUT_DB = "staging_tables.duckdb"      # base staging generee

# nom du modele -> SQL (copie fidele des modeles dbt de Marouane)
MODELS = {
    "stg_assessments": """
        select
            id_assessment, code_module, code_presentation, assessment_type,
            try_cast(nullif(date, '?') as integer) as assessment_day,
            weight as assessment_weight
        from raw.assessments
    """,
    "stg_courses": """
        select
            code_module, code_presentation,
            module_presentation_length as course_length_days
        from raw.courses
    """,
    "stg_student_assessment": """
        select
            id_assessment, id_student, date_submitted, is_banked,
            try_cast(nullif(score, '?') as integer) as score
        from raw.student_assessment
    """,
    "stg_student_info": """
        select
            code_module, code_presentation, id_student,
            code_module || '-' || code_presentation || '-' || id_student as student_presentation_id,
            nullif(gender, '?') as gender,
            nullif(region, '?') as region,
            nullif(highest_education, '?') as highest_education,
            case
                when imd_band = '?' or imd_band is null then null
                when imd_band like '%\\%' escape '\\' then imd_band
                else imd_band || '%'
            end as imd_band,
            nullif(age_band, '?') as age_band,
            num_of_prev_attempts, studied_credits,
            nullif(disability, '?') as disability,
            final_result
        from raw.student_info
    """,
    "stg_student_registration": """
        select
            code_module, code_presentation, id_student,
            code_module || '-' || code_presentation || '-' || id_student as student_presentation_id,
            try_cast(nullif(date_registration, '?') as integer) as date_registration,
            try_cast(nullif(date_unregistration, '?') as integer) as date_unregistration
        from raw.student_registration
    """,
    "stg_student_vle": """
        select
            code_module, code_presentation, id_student, id_site,
            date as interaction_day, sum_click
        from raw.student_vle
    """,
    "stg_vle": """
        select
            id_site, code_module, code_presentation, activity_type,
            try_cast(nullif(week_from, '?') as integer) as week_from,
            try_cast(nullif(week_to, '?') as integer) as week_to
        from raw.vle
    """,
}


def main():
    con = duckdb.connect(OUT_DB)
    # Attacher la base raw d'Aymen
    con.execute(f"ATTACH '{SRC_DB}' AS src (READ_ONLY)")
    con.execute("CREATE SCHEMA IF NOT EXISTS staging")

    print("Materialisation de la couche STAGING...\n")
    for model_name, sql in MODELS.items():
        # rendre les references raw.X pointant vers la base attachee 'src'
        sql_resolved = re.sub(r"\braw\.", "src.raw.", sql)
        con.execute(f"CREATE OR REPLACE TABLE staging.{model_name} AS {sql_resolved}")
        n = con.execute(f"SELECT COUNT(*) FROM staging.{model_name}").fetchone()[0]
        print(f"  [OK] staging.{model_name:<28} {n:>12,} lignes")

    con.execute("DETACH src")
    con.close()
    print(f"\nBase staging generee : {OUT_DB}")


if __name__ == "__main__":
    main()
