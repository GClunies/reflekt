{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'enriched_session') }}

),

renamed as (

    select
        id as event_id,
        'surfline'::varchar as source_schema,
        'enriched_session'::varchar as source_table,
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
        client,
        condition,
        current_tide_height,
        max_distance,
        max_speed,
        next_tide_height,
        session_id,
        session_length,
        spot_id,
        spot_name,
        spot_relive_rating,
        start_lat_lon,
        start_timestamp,
        stop_timestamp,
        wave_count,
        wave_height_max,
        wave_height_min,
        wind_direction,
        wind_speed

    from source

)

select * from renamed
