{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select * from {{ source('my_app_web', 'product_added') }}
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
        context_ip as ip,
        context_library_name as library_name,
        context_library_version as library_version,
        context_page_path as page_path,
        context_page_referrer as page_referrer,
        context_page_title as page_title,
        context_page_url as page_url,
        context_user_agent as user_agent,
        cart_id,
        name,
        price,
        product_id,
        quantity,
        variant
    from source
)

select * from renamed