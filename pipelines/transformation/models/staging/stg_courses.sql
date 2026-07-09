-- One row per course (module) presentation.
select
    code_module,
    code_presentation,
    module_presentation_length as course_length_days
from {{ source('raw', 'courses') }}
