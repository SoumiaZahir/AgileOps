-- =============================================================================
-- FINAL MODELING TABLE — grain: one row per student per course presentation.
-- Consumed by Abderahman (ML training) and Brahim (dashboards).
--
-- BUSINESS RULE (assumption — confirm with Aymen/PO + Abderahman before
-- training): label_pass = 1 for 'Pass' and 'Distinction', 0 for 'Fail' and
-- 'Withdrawn'. Withdrawn students are treated as a negative outcome since
-- they did not complete/pass the course. If the team wants to model
-- withdrawal separately from failure, split label_pass into two flags here.
-- =============================================================================
with student_info as (
    select * from {{ ref('stg_student_info') }}
),
courses as (
    select * from {{ ref('dim_courses') }}
),
registration as (
    select * from {{ ref('int_student_registration_clean') }}
),
assessment_features as (
    select * from {{ ref('int_student_assessment_agg') }}
),
vle_features as (
    select * from {{ ref('int_student_vle_agg') }}
)

select
    si.student_presentation_id,
    si.code_module,
    si.code_presentation,
    si.id_student,

    -- demographics
    si.gender,
    si.region,
    si.highest_education,
    si.imd_band,
    si.age_band,
    si.disability,
    si.num_of_prev_attempts,
    si.studied_credits,

    -- course context
    c.course_length_days,

    -- registration behavior
    r.date_registration,
    r.registered_before_course_start,
    r.is_unregistered,

    -- assessment performance
    coalesce(af.n_assessments_submitted, 0) as n_assessments_submitted,
    af.weighted_avg_score,
    af.avg_score,
    coalesce(af.n_late_submissions, 0) as n_late_submissions,
    coalesce(af.n_banked_assessments, 0) as n_banked_assessments,

    -- VLE engagement
    coalesce(vf.n_active_days, 0) as n_active_days,
    coalesce(vf.total_clicks, 0) as total_clicks,
    coalesce(vf.n_distinct_materials_accessed, 0) as n_distinct_materials_accessed,

    -- target
    si.final_result,
    case
        when si.final_result in ('Pass', 'Distinction') then 1
        when si.final_result in ('Fail', 'Withdrawn') then 0
    end as label_pass

from student_info si
left join courses c
    on si.code_module = c.code_module
    and si.code_presentation = c.code_presentation
left join registration r
    on si.student_presentation_id = r.student_presentation_id
left join assessment_features af
    on si.student_presentation_id = af.student_presentation_id
left join vle_features vf
    on si.student_presentation_id = vf.student_presentation_id
