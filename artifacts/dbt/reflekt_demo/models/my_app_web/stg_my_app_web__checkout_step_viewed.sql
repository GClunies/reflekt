{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select * from {{ source('my_app_web', 'checkout_step_viewed') }}
),

renamed as (
    select
        id as event_id,
        original_timestamp as original_tstamp,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        anonymous_id,
        user_id,
        context_library_name as library_name,
        context_library_version as library_version,
        checkout_id,
        shipping_method,
        step
    from source
)

select * from renamed