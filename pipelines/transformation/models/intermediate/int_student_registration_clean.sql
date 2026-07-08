-- Grain: one row per student per course presentation.
-- Adds derived registration-timing flags used as early-warning features.
select
    code_module,
    code_presentation,
    id_student,
    student_presentation_id,
    date_registration,
    date_unregistration,
    case when date_unregistration is not null then 1 else 0 end as is_unregistered,
    case when date_registration is not null and date_registration < 0 then 1 else 0 end
        as registered_before_course_start
from {{ ref('stg_student_registration') }}
