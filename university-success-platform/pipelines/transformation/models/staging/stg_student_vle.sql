-- Clickstream fact: one row per (student, material, day) with click count.
-- Largest raw table (~10.6M rows) — kept as a view, aggregated in the
-- intermediate layer rather than materialized wide.
select
    code_module,
    code_presentation,
    id_student,
    id_site,
    date as interaction_day,
    sum_click
from {{ source('raw', 'student_vle') }}
