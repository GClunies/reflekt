{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('buoyweather_web', 'purchased_gift_card') }}

),

renamed as (

    select
        id as event_id,
        'buoyweather'::varchar as source_schema,
        'purchased_gift_card'::varchar as source_table,
        'buoyweather-web'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        anonymous_id,
        amount,
        currency,
        description,
        message,
        plan_id,
        platform,
        price_id,
        purchase_date,
        purchaser_email,
        purchaser_name,
        recipient_name,
        recipientemail,
        redeem_code

    from source

)

select * from renamed
