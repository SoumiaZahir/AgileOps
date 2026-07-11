"""
06_build_staging_suites.py
----------------------------
Construit les Expectation Suites pour la couche STAGING (modeles dbt de
Marouane, materialises via scripts/build_staging_tables.py).

La couche staging nettoie les '?' du raw (-> NULL) et caste les colonnes
numeriques. Les regles ci-dessous verifient que ce nettoyage a bien eu lieu :
  - les colonnes numeriques sont desormais dans des plages valides ;
  - imd_band est standardise (toujours avec '%') ;
  - les cles restent non nulles / uniques.

A executer depuis data_quality/project/ (apres build_staging_tables.py) :
    python scripts/06_build_staging_suites.py
"""

import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.exceptions.exceptions import DataContextError
import great_expectations.expectations as gxe


def add_or_replace_suite(context, name):
    try:
        suite = context.suites.get(name)
        for exp in list(suite.expectations):
            suite.delete_expectation(exp)
    except (KeyError, LookupError, DataContextError):
        suite = ExpectationSuite(name=name)
        context.suites.add(suite)
    return suite


def build_stg_courses(context):
    s = add_or_replace_suite(context, "staging_stg_courses_suite")
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_module"))
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_presentation"))
    s.add_expectation(gxe.ExpectColumnValuesToMatchRegex(column="code_presentation", regex=r"^\d{4}[BJ]$"))
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="course_length_days", min_value=1, max_value=365))
    s.add_expectation(gxe.ExpectCompoundColumnsToBeUnique(column_list=["code_module", "code_presentation"]))
    return s


def build_stg_assessments(context):
    s = add_or_replace_suite(context, "staging_stg_assessments_suite")
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_assessment"))
    s.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="id_assessment"))
    s.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="assessment_type", value_set=["TMA", "CMA", "Exam"]))
    # assessment_day : desormais INTEGER (les '?' -> NULL). Plage realiste.
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="assessment_day", min_value=0, max_value=400))
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="assessment_weight", min_value=0, max_value=100))
    return s


def build_stg_student_info(context):
    s = add_or_replace_suite(context, "staging_stg_student_info_suite")
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="student_presentation_id"))
    s.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="student_presentation_id"))
    s.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="gender", value_set=["M", "F"]))
    s.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="disability", value_set=["Y", "N"]))
    s.add_expectation(gxe.ExpectColumnValuesToBeInSet(
        column="final_result", value_set=["Pass", "Fail", "Withdrawn", "Distinction"]))
    # Verification du nettoyage : imd_band doit desormais etre standardise
    # avec '%' (plus de "10-20" brut, plus de '?'). NULL autorise.
    s.add_expectation(gxe.ExpectColumnValuesToBeInSet(
        column="imd_band",
        value_set=["0-10%", "10-20%", "20-30%", "30-40%", "40-50%",
                   "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]))
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="num_of_prev_attempts", min_value=0, max_value=10))
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="studied_credits", min_value=0, max_value=1000))
    return s


def build_stg_student_registration(context):
    s = add_or_replace_suite(context, "staging_stg_student_registration_suite")
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    s.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="student_presentation_id"))
    # date_registration : desormais INTEGER, valeurs negatives valides
    # (inscription avant le debut du cours). NULL autorise.
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="date_registration", min_value=-400, max_value=400))
    return s


def build_stg_student_assessment(context):
    s = add_or_replace_suite(context, "staging_stg_student_assessment_suite")
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_assessment"))
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    s.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="is_banked", value_set=[0, 1]))
    # score : desormais INTEGER 0-100 (les '?' -> NULL). NULL autorise.
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="score", min_value=0, max_value=100))
    return s


def build_stg_vle(context):
    s = add_or_replace_suite(context, "staging_stg_vle_suite")
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_site"))
    s.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="id_site"))
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="activity_type"))
    # week_from / week_to : INTEGER apres nettoyage. Beaucoup de NULL (~82%),
    # attendu -> pas de contrainte de completude, juste la plage.
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="week_from", min_value=0, max_value=52))
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="week_to", min_value=0, max_value=52))
    return s


def build_stg_student_vle(context):
    s = add_or_replace_suite(context, "staging_stg_student_vle_suite")
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    s.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_site"))
    s.add_expectation(gxe.ExpectColumnValuesToBeBetween(column="sum_click", min_value=1, max_value=20000))
    return s


BUILDERS = [
    build_stg_courses, build_stg_assessments, build_stg_student_info,
    build_stg_student_registration, build_stg_student_assessment,
    build_stg_vle, build_stg_student_vle,
]


def main():
    context = gx.get_context(mode="file", project_root_dir=".")
    print("Construction des Expectation Suites (couche STAGING)...\n")
    for b in BUILDERS:
        s = b(context)
        print(f"  [OK] {s.name} -> {len(s.expectations)} regles")
    print("\nSuites staging creees avec succes.")


if __name__ == "__main__":
    main()
