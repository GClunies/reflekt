{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select *
    from {{ source('jaffle_shop_segment', 'pages') }}
    where received_at < getdate()
),

renamed as (
    select
        id as page_id,
        original_timestamp as original_tstamp,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        user_id,
        context_library_name as library_name,
        context_library_version as library_version,
        context_page_path as page_path,
        context_page_referrer as page_referrer,
        context_page_title as page_title,
        context_page_url as page_url,
        context_protocols_source_id as protocols_source_id,
        context_protocols_violations as protocols_violations,
        context_protocols_omitted as protocols_omitted,
        name,
        cart_id,
        name as _name,
        order_id,
        path,
        product_id,
        referrer,
        session_id,
        title,
        url,
        'page'::varchar as call_type,
        'jaffle_shop_segment'::varchar as source_schema,
        'pages'::varchar as source_table,
        'jaffle_shop/Page_Viewed/1-0.json'::varchar as schema_id
    from source
)

select * from renamed
