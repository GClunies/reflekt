{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select * from {{ source('my_app_web', 'order_completed') }}
),

renamed as (
    select
        id,
        original_timestamp as original_tstamp,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        anonymous_id,
        user_id,
        context_library_name as library_name,
        context_library_version as library_version,
        checkout_id,
        currency,
        order_id,
        products,
        revenue,
        shipping,
        tax
    from source
)

select * from renamed