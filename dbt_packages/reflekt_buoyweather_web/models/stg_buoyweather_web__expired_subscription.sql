{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('buoyweather_web', 'expired_subscription') }}

),

renamed as (

    select
        id as event_id,
        'buoyweather'::varchar as source_schema,
        'expired_subscription'::varchar as source_table,
        'buoyweather-web'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        user_id,
        context_protocols_source_id as segment_protocols_source_id,
        context_protocols_violations as segment_protocols_violations,
        active,
        billing_platform,
        country,
        current_period_end,
        current_period_start,
        entitlement,
        expiration,
        in_trial,
        interval,
        interval_count,
        plan_id,
        platform,
        promotion_id,
        reason,
        seconds_remaining,
        subscription_id,
        trial_eligible

    from source

)

select * from renamed
