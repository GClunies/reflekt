{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select *
    from {{ source('ecomm_demo', 'pages') }}
    where received_at < current_date
),

renamed as (
    select
        id as page_id,
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
        context_page_search as page_search,
        context_page_title as page_title,
        context_page_url as page_url,
        context_user_agent as user_agent,
        path,
        referrer,
        search,
        title,
        url,
        'page'::varchar as call_type,
        'ecomm_demo'::varchar as source_schema,
        'pages'::varchar as source_table,
        'segment/ecommerce/Page Viewed/1-0.json'::varchar as schema_id,
        '{"code_owner": "Maura", "product_owner": "Greg"}'::varchar as schema_metadata
    from source
)

select * from renamed