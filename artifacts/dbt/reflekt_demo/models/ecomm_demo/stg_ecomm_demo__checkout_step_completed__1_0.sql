{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select * from {{ source('ecomm_demo', 'checkout_step_completed') }}
),

renamed as (
    select
        id as event_id,
        event_text as event_name,
        original_timestamp as original_tstamp,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        anonymous_id,
        user_id,
        context_library_name as library_name,
        context_library_version as library_version,
        checkout_id,
        step,
        'track'::varchar as call_type,
        'ecomm_demo'::varchar as source_schema,
        'checkout_step_completed'::varchar as source_table,
        'segment/ecommerce/Checkout Step Completed/1-0.json'::varchar as schema_id
    from source
)

select * from renamed