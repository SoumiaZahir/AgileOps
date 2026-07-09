-- VLE material catalog: one row per site/material available in a presentation.
select
    id_site,
    code_module,
    code_presentation,
    activity_type,
    try_cast(nullif(week_from, '?') as integer) as week_from,
    try_cast(nullif(week_to, '?') as integer) as week_to
from {{ source('raw', 'vle') }}
