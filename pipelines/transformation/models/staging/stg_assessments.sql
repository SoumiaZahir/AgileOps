-- One row per assessment definition. OULAD encodes missing values as the
-- literal string '?', so every numeric column is cleaned with nullif + try_cast.
select
    id_assessment,
    code_module,
    code_presentation,
    assessment_type,
    try_cast(nullif(date, '?') as integer) as assessment_day,
    -- NOTE: unlike `date`, the raw `weight` column is already typed DOUBLE
    -- by DuckDB's CSV auto-detection (no '?' placeholders in this column),
    -- so no nullif() is needed/possible here.
    weight as assessment_weight
from {{ source('raw', 'assessments') }}
