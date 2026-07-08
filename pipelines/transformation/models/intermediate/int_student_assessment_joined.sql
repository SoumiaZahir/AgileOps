-- Grain: one row per assessment submission, enriched with the assessment's
-- weight/type/due-day so lateness and weighted scores can be computed.
with student_assessment as (
    select * from {{ ref('stg_student_assessment') }}
),
assessments as (
    select * from {{ ref('stg_assessments') }}
)

select
    sa.id_student,
    a.code_module,
    a.code_presentation,
    a.id_assessment,
    a.assessment_type,
    a.assessment_day,
    a.assessment_weight,
    sa.date_submitted,
    sa.score,
    sa.is_banked,
    case
        when a.assessment_day is not null and sa.date_submitted > a.assessment_day
            then 1 else 0
    end as is_late_submission
from student_assessment sa
inner join assessments a on sa.id_assessment = a.id_assessment
