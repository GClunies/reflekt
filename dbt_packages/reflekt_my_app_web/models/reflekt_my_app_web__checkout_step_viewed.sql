{{
  config(
    materialized = 'incremental',
    unique_key = 'event_id',
    cluster_by = 'tstamp'
  )
}}

with

source as (

    select *

    from {{ source('my_app_web', 'checkout_step_viewed') }}
    {%- if is_incremental() %}
    where received_at >= ( select max(received_at_tstamp)::date from {{ this }} )
    {%- endif %}

),

renamed as (

    select
        id as event_id,
        'patty_bar_web'::varchar as source_schema,
        'checkout_step_viewed'::varchar as source_table,
        'my-plan'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        anonymous_id,
        user_id,
        checkout_id,
        payment_method,
        shipping_method,
        step

    from source

)

select * from renamed
