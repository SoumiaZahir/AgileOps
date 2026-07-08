-- Registration / unregistration day offsets, relative to course start (day 0).
-- Negative values are valid in OULAD (student registered before the course
-- officially started) — kept as-is, flagged downstream in the intermediate layer.
select
    code_module,
    code_presentation,
    id_student,
    code_module || '-' || code_presentation || '-' || id_student as student_presentation_id,
    try_cast(nullif(date_registration, '?') as integer) as date_registration,
    try_cast(nullif(date_unregistration, '?') as integer) as date_unregistration
from {{ source('raw', 'student_registration') }}
