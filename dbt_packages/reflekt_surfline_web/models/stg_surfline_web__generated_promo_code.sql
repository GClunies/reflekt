{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'generated_promo_code') }}

),

renamed as (

    select
        id as event_id,
        'surfline'::varchar as source_schema,
        'generated_promo_code'::varchar as source_table,
        'surfline-web'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        user_id,
        context_protocols_source_id as segment_protocols_source_id,
        code,
        platform,
        promo_codes_available,
        type

    from source

)

select * from renamed
