{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('buoyweather_web', 'users') }}

),

renamed as (

    select
        id as user_id,
        'buoyweather'::varchar as source_schema,
        'users'::varchar as source_table,
        'buoyweather-web'::varchar as tracking_plan,
        received_at as received_at_tstamp,
        user_id

    from source

)

select * from renamed
