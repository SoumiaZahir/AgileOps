-- Grain: one row per student per course presentation.
-- Aggregates clickstream engagement (from the ~10.6M row fact) into features.
select
    code_module,
    code_presentation,
    id_student,
    code_module || '-' || code_presentation || '-' || id_student as student_presentation_id,
    count(distinct id_site) as n_distinct_materials_accessed,
    count(distinct interaction_day) as n_active_days,
    sum(sum_click) as total_clicks,
    min(interaction_day) as first_interaction_day,
    max(interaction_day) as last_interaction_day
from {{ ref('stg_student_vle') }}
group by 1, 2, 3, 4
