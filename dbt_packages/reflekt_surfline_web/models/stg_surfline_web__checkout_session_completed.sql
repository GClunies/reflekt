{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'checkout_session_completed') }}

),

renamed as (

    select
        id as event_id,
        'surfline'::varchar as source_schema,
        'checkout_session_completed'::varchar as source_table,
        'surfline-web'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        user_id,
        context_protocols_source_id as segment_protocols_source_id,
        context_protocols_violations as segment_protocols_violations,
        after_expiration,
        allow_promotion_codes,
        amount_subtotal,
        amount_total,
        currency,
        customer,
        customer_email,
        locale,
        mode,
        payment_intent,
        payment_status,
        recovered_from,
        setup_intent,
        subscription,
        success_url

    from source

)

select * from renamed
