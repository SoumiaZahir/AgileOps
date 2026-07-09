-- One row per assessment submission. score is 0-100, '?' means not yet scored.
select
    id_assessment,
    id_student,
    date_submitted,
    is_banked,
    try_cast(nullif(score, '?') as integer) as score
from {{ source('raw', 'student_assessment') }}
