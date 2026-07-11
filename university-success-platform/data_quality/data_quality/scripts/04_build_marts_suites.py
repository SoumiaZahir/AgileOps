"""
04_build_marts_suites.py
--------------------------
Construit les Expectation Suites pour la couche MARTS produite par Marouane
(sortie dbt) : `student_success_features` et `dim_courses`.

Complete la validation Raw (scripts 01-03) en couvrant la couche finale
utilisee directement par Abderahman (modele) et Brahim (dashboards).

Les regles sont basees sur le profilage reel des CSV marts + le data
dictionary fourni par Marouane
(docs/data_dictionary_student_success_features.md).

A executer depuis data_quality/project/ :
    python scripts/04_build_marts_suites.py
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


def build_student_success_features_suite(context):
    suite = add_or_replace_suite(context, "marts_student_success_features_suite")

    # --- Cle & identifiants ---
    suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(column="student_presentation_id")
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeUnique(column="student_presentation_id")
    )
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="id_student"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_module"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_presentation"))
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(
            column="code_presentation", regex=r"^\d{4}[BJ]$"
        )
    )

    # --- Variable cible (la plus critique pour la modelisation) ---
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="label_pass"))
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(column="label_pass", value_set=[0, 1])
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column="final_result",
            value_set=["Pass", "Fail", "Withdrawn", "Distinction"],
        )
    )

    # --- Variables categorielles ---
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(column="gender", value_set=["M", "F"])
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(column="disability", value_set=["Y", "N"])
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column="age_band", value_set=["0-35", "35-55", "55<="]
        )
    )
    # imd_band : desormais standardise avec '%' (Marouane a corrige) et NULL
    # autorise pour les valeurs inconnues. On verifie le format propre.
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column="imd_band",
            value_set=[
                "0-10%", "10-20%", "20-30%", "30-40%", "40-50%",
                "50-60%", "60-70%", "70-80%", "80-90%", "90-100%",
            ],
        )
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column="highest_education",
            value_set=[
                "A Level or Equivalent", "HE Qualification",
                "Lower Than A Level", "No Formal quals",
                "Post Graduate Qualification",
            ],
        )
    )

    # --- Flags binaires ---
    for col in ["registered_before_course_start", "is_unregistered"]:
        suite.add_expectation(gxe.ExpectColumnValuesToBeInSet(column=col, value_set=[0, 1]))

    # --- Plages numeriques (features) ---
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="num_of_prev_attempts", min_value=0, max_value=10)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="studied_credits", min_value=0, max_value=1000)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="course_length_days", min_value=1, max_value=365)
    )
    # Scores : entre 0 et 100. NULL tolere (voir note ci-dessous) via mostly.
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="weighted_avg_score", min_value=0, max_value=100)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="avg_score", min_value=0, max_value=100)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="n_assessments_submitted", min_value=0, max_value=50)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="n_late_submissions", min_value=0, max_value=50)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="n_active_days", min_value=0, max_value=400)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="total_clicks", min_value=0, max_value=100000)
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="n_distinct_materials_accessed", min_value=0, max_value=1000)
    )

    # --- Surveillance du taux de valeurs manquantes sur weighted_avg_score ---
    # Documente dans le data dictionary : ~28% de NULL (etudiants sans
    # evaluation notee). C'est ATTENDU mais critique pour la modelisation :
    # on pose une expectation qui echoue si le taux depasse 35%, pour
    # detecter toute derive future (regression de qualite en amont).
    suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(column="weighted_avg_score", mostly=0.65)
    )

    return suite


def build_dim_courses_suite(context):
    suite = add_or_replace_suite(context, "marts_dim_courses_suite")
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="course_presentation_id"))
    suite.add_expectation(gxe.ExpectColumnValuesToBeUnique(column="course_presentation_id"))
    suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="code_module"))
    suite.add_expectation(
        gxe.ExpectColumnValuesToMatchRegex(column="code_presentation", regex=r"^\d{4}[BJ]$")
    )
    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(column="course_length_days", min_value=1, max_value=365)
    )
    return suite


def main():
    context = gx.get_context(mode="file", project_root_dir=".")
    print("Construction des Expectation Suites (couche MARTS)...\n")

    s1 = build_student_success_features_suite(context)
    print(f"  [OK] {s1.name} -> {len(s1.expectations)} regles")

    s2 = build_dim_courses_suite(context)
    print(f"  [OK] {s2.name} -> {len(s2.expectations)} regles")

    print("\nSuites Marts creees avec succes.")


if __name__ == "__main__":
    main()
