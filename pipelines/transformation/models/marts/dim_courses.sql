-- Dimension table: one row per course (module) presentation.
select
    code_module,
    code_presentation,
    code_module || '-' || code_presentation as course_presentation_id,
    course_length_days
from {{ ref('stg_courses') }}
