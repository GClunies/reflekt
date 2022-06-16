{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'days_to_convert_from_trial') }}

),

renamed as (

    select
        id as event_id,
        'surfline'::varchar as source_schema,
        'days_to_convert_from_trial'::varchar as source_table,
        'surfline-web'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        user_id,
        context_protocols_source_id as segment_protocols_source_id,
        context_protocols_violations as segment_protocols_violations,
        context_protocols_omitted as segment_protocols_omitted_properties,
        card_type,
        days_to_premium,
        plan_id,
        platform

    from source

)

select * from renamed
