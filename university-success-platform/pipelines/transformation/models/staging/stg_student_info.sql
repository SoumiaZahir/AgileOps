-- One row per student per course presentation: demographics + final outcome.
-- imd_band arrives with inconsistent formatting in the source CSV
-- ("10-20" vs "0-10%") — standardized here to always include the % sign.
select
    code_module,
    code_presentation,
    id_student,
    code_module || '-' || code_presentation || '-' || id_student as student_presentation_id,
    nullif(gender, '?') as gender,
    nullif(region, '?') as region,
    nullif(highest_education, '?') as highest_education,
    case
        when imd_band = '?' or imd_band is null then null
        when imd_band like '%\%' escape '\' then imd_band
        else imd_band || '%'
    end as imd_band,
    nullif(age_band, '?') as age_band,
    num_of_prev_attempts,
    studied_credits,
    nullif(disability, '?') as disability,
    final_result
from {{ source('raw', 'student_info') }}
