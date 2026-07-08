# Data Dictionary — `marts.student_success_features`

Grain: **one row per student per course presentation** (32,593 rows).
Source: OULAD (Open University Learning Analytics Dataset), via Aymen's
raw ingestion → Marouane's dbt transformation.

| Column | Type | Description |
|---|---|---|
| student_presentation_id | varchar | Surrogate key: `code_module-code_presentation-id_student`. |
| code_module | varchar | Course/module code (e.g. `AAA`). |
| code_presentation | varchar | Semester code (e.g. `2013J` = Oct 2013 start). |
| id_student | bigint | Student ID. |
| gender | varchar | `M` / `F`. |
| region | varchar | Student's geographic region. |
| highest_education | varchar | Highest prior education level. |
| imd_band | varchar | Deprivation index band of student's home area (`0-10%` ... `90-100%`), NULL if unknown. |
| age_band | varchar | Age bracket. |
| disability | varchar | `Y` / `N`. |
| num_of_prev_attempts | bigint | Number of prior attempts at this module. |
| studied_credits | bigint | Total credits the student is studying that term. |
| course_length_days | bigint | Length of the course presentation, in days. |
| date_registration | integer | Days relative to course start when the student registered (can be negative — registered early). NULL if unknown. |
| registered_before_course_start | integer (0/1) | 1 if `date_registration < 0`. |
| is_unregistered | integer (0/1) | 1 if the student unregistered before the presentation ended. |
| n_assessments_submitted | bigint | Count of assessments the student submitted. |
| weighted_avg_score | double | `sum(score * weight) / sum(weight)` over scored assessments. **NULL for ~28% of students** (7 in TMA/CMA who submitted nothing scored) — flag for Abderahman: needs an explicit imputation/missing-indicator strategy, don't silently drop or zero-fill. |
| avg_score | double | Simple (unweighted) average score. |
| n_late_submissions | bigint | Count of assessments submitted after the due day. |
| n_banked_assessments | bigint | Count of assessments carried over ("banked") from a previous attempt. |
| n_active_days | bigint | Distinct days the student clicked on any VLE material. |
| total_clicks | bigint | Sum of `sum_click` across all VLE interactions. |
| n_distinct_materials_accessed | bigint | Distinct VLE material IDs (`id_site`) touched. |
| final_result | varchar | Raw outcome: `Pass`, `Fail`, `Withdrawn`, `Distinction`. |
| label_pass | integer (0/1) | **Target variable.** 1 = Pass/Distinction, 0 = Fail/Withdrawn. See the assumption note below. |

## Business-rule assumption to confirm with the team

`label_pass` currently treats `Withdrawn` the same as `Fail` (both → 0).
This is a reasonable default but it's a modeling decision, not a fact —
confirm it with Aymen (Product Owner) and Abderahman (ML) before training:

- If the team wants "did the student complete AND pass" → keep as-is.
- If withdrawal should be excluded entirely (only predict pass/fail among
  completers) → filter `final_result != 'Withdrawn'` before training, or
  ask Marouane to add a second column `label_pass_excl_withdrawn`.

## Known data-quality notes (already handled in staging, listed for transparency)

- OULAD uses the literal string `'?'` for missing values in several raw
  columns (`assessments.date`, `student_registration.date_registration` /
  `date_unregistration`, `student_assessment.score`, `vle.week_from` /
  `week_to`, `student_info.imd_band`) — all converted to real `NULL`s in staging.
- `imd_band` formatting was inconsistent in the raw CSV (`10-20` vs `0-10%`)
  — standardized to always include `%`.
