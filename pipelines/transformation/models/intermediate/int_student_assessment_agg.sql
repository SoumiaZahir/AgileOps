-- Grain: one row per student per course presentation.
-- Aggregates assessment performance into modeling features.
-- weighted_avg_score follows OULAD convention: sum(score*weight)/sum(weight)
-- over assessments that were actually scored (NULL scores excluded).
select
    code_module,
    code_presentation,
    id_student,
    code_module || '-' || code_presentation || '-' || id_student as student_presentation_id,
    count(*) as n_assessments_submitted,
    sum(case when score is null then 1 else 0 end) as n_assessments_missing_score,
    sum(is_late_submission) as n_late_submissions,
    sum(is_banked) as n_banked_assessments,
    round(
        sum(coalesce(score, 0) * assessment_weight)
        / nullif(sum(case when score is not null then assessment_weight else 0 end), 0)
    , 2) as weighted_avg_score,
    round(avg(score), 2) as avg_score,
    min(score) as min_score,
    max(score) as max_score
from {{ ref('int_student_assessment_joined') }}
group by 1, 2, 3, 4
