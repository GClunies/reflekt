{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('buoyweather_web', 'redeemed_gift_card') }}

),

renamed as (

    select
        id as event_id,
        'buoyweather'::varchar as source_schema,
        'redeemed_gift_card'::varchar as source_table,
        'buoyweather-web'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        user_id,
        context_protocols_source_id as segment_protocols_source_id,
        context_protocols_violations as segment_protocols_violations,
        plan_id,
        platform,
        redeem_code

    from source

)

select * from renamed
