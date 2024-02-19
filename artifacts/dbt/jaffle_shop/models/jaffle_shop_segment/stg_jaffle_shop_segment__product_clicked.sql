{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select *
    from {{ source('jaffle_shop_segment', 'product_clicked') }}
    where received_at < getdate()
),

renamed as (
    select
        id as event_id,
        event_text as event_name,
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
        name,
        session_id,
        product_id,
        sku,
        category,
        name as _name,
        price,
        'track'::varchar as call_type,
        'jaffle_shop_segment'::varchar as source_schema,
        'product_clicked'::varchar as source_table,
        'jaffle_shop/Product_Clicked/1-0.json'::varchar as schema_id
    from source
)

select * from renamed
