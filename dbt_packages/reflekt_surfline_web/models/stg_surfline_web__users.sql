{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'users') }}

),

renamed as (

    select
        id as user_id,
        'surfline'::varchar as source_schema,
        'users'::varchar as source_table,
        'surfline-web'::varchar as tracking_plan,
        received_at as received_at_tstamp

    from source

)

select * from renamed
