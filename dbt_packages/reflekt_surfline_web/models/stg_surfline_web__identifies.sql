{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'identifies') }}

),

renamed as (

    select
        id as event_id,
        'surfline'::varchar as source_schema,
        'identifies'::varchar as source_table,
        'surfline-web'::varchar as tracking_plan,
        received_at as received_at_tstamp,
        sent_at as sent_at_tstamp,
        "timestamp" as tstamp,
        anonymous_id,
        user_id

    from source

)

select * from renamed
