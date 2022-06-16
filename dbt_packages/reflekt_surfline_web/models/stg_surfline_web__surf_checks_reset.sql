{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'surf_checks_reset') }}

),

renamed as (

    select
        id as event_id,
        'surfline'::varchar as source_schema,
        'surf_checks_reset'::varchar as source_table,
        'surfline-web'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        anonymous_id,
        user_id,
        context_protocols_source_id as segment_protocols_source_id,
        context_protocols_violations as segment_protocols_violations,
        context_protocols_omitted as segment_protocols_omitted_properties,
        checks_available,
        meter_id,
        platform

    from source

)

select * from renamed
