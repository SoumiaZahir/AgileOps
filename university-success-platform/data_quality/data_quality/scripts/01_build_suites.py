"""
01_build_suites.py
-------------------
Construit les Expectation Suites Great Expectations pour chaque table
raw du dataset OULAD (Open University Learning Analytics Dataset).

Auteur : Imane Alouani - Data Quality Specialist
Projet  : Smart Platform for University Success

A executer depuis le dossier data_quality/project/ :
    python scripts/01_build_suites.py
"""

import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.exceptions.exceptions import DataContextError
import great_expectations.expectations as gxe

DB_PATH = "university.duckdb"
CONNECTION_STRING = f"duckdb:///{DB_PATH}"


def get_context():
    return gx.get_context(mode="file", project_root_dir=".")


def get_or_add_datasource(context):
    try:
        return context.data_sources.get("university_db")
    except (KeyError, LookupError, DataContextError):
        return context.data_sources.add_sql(
            name="university_db", connection_string=CONNECTION_STRING
        )


def add_or_replace_suite(context, name):
    try:
        suite = context.suites.get(name)
        for exp in list(suite.expectations):
            suite.delete_expectation(exp)
    except (KeyError, LookupError, DataContextError):
        suite = ExpectationSuite(name=name)
        context.suites.add(suite)
    return suite


def build_courses_suite(context):
    suite = add_or_replace_suite(context, "courses_suite")
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_module"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_presentation"))
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(column="code_presentation", regex=r"^\d{4}[BJ]$")
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(
            column="module_presentation_length", min_value=1, max_value=365
        )
    )
    suite.add_expectation(
        gxe.ExpectCompoundColumnsToBeUnique(column_list=["code_module", "code_presentation"])
    )
    return suite


def build_assessments_suite(context):
    suite = add_or_replace_suite(context, "assessments_suite")
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_assessment"))
    suite.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="id_assessment"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_module"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_presentation"))
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(column="assessment_type", value_set=["TMA", "CMA", "Exam"])
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="weight", min_value=0, max_value=100)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(column="date", regex=r"^(\?|-?\d+)$")
    )
    # Regle metier : max 2% de dates manquantes ('?'). Anomalie reelle : 5,3%.
    suite.add_expectation(
        gxe.ExpectColumnValuesToNotMatchRegex(column="date", regex=r"^\?$", mostly=0.98)
    )
    return suite


def build_student_info_suite(context):
    suite = add_or_replace_suite(context, "student_info_suite")
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_module"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_presentation"))
    suite.add_expectation(
        gxe.ExpectCompoundColumnsToBeUnique(
            column_list=["code_module", "code_presentation", "id_student"]
        )
    )
    suite.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="gender", value_set=["M", "F"]))
    suite.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="disability", value_set=["Y", "N"]))
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column="final_result", value_set=["Pass", "Fail", "Withdrawn", "Distinction"]
        )
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column="imd_band",
            value_set=[
                "0-10%", "10-20", "20-30%", "30-40%", "40-50%", "50-60%",
                "60-70%", "70-80%", "80-90%", "90-100%", "?",
            ],
        )
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="num_of_prev_attempts", min_value=0, max_value=10)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="studied_credits", min_value=0, max_value=1000)
    )
    return suite


def build_student_registration_suite(context):
    suite = add_or_replace_suite(context, "student_registration_suite")
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    suite.add_expectation(
        gxe.ExpectCompoundColumnsToBeUnique(
            column_list=["code_module", "code_presentation", "id_student"]
        )
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(column="date_registration", regex=r"^(\?|-?\d+)$")
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(column="date_unregistration", regex=r"^(\?|-?\d+)$")
    )
    return suite


def build_student_assessment_suite(context):
    suite = add_or_replace_suite(context, "student_assessment_suite")
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_assessment"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    suite.add_expectation(gxe.ExpectColumnValuesToBeInSet(column="is_banked", value_set=[0, 1]))
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(column="score", regex=r"^(\?|\d{1,3})$")
    )
    return suite


def build_vle_suite(context):
    suite = add_or_replace_suite(context, "vle_suite")
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_site"))
    suite.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="id_site"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="activity_type"))
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(column="week_from", regex=r"^(\?|-?\d+)$")
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(column="week_to", regex=r"^(\?|-?\d+)$")
    )
    # Anomalie majeure : ~82% de '?'. Seuil a 50% pour la faire remonter.
    suite.add_expectation(
        gxe.ExpectColumnValuesToNotMatchRegex(column="week_from", regex=r"^\?$", mostly=0.50)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToNotMatchRegex(column="week_to", regex=r"^\?$", mostly=0.50)
    )
    return suite


def build_student_vle_suite(context):
    suite = add_or_replace_suite(context, "student_vle_suite")
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_site"))
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="sum_click", min_value=1, max_value=20000)
    )
    return suite


TABLE_BUILDERS = {
    "courses": build_courses_suite,
    "assessments": build_assessments_suite,
    "student_info": build_student_info_suite,
    "student_registration": build_student_registration_suite,
    "student_assessment": build_student_assessment_suite,
    "vle": build_vle_suite,
    "student_vle": build_student_vle_suite,
}


def main():
    context = get_context()
    get_or_add_datasource(context)
    print("Construction des Expectation Suites (couche RAW)...\n")
    for table_name, builder in TABLE_BUILDERS.items():
        suite = builder(context)
        print(f"  [OK] {suite.name} -> {len(suite.expectations)} regles")
    print("\nToutes les suites raw ont ete creees / mises a jour avec succes.")


if __name__ == "__main__":
    main()
