{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'invalid_forgot_password_reset_code') }}

),

renamed as (

    select
        id as event_id,
        'surfline'::varchar as source_schema,
        'invalid_forgot_password_reset_code'::varchar as source_table,
        'surfline-web'::varchar as tracking_plan,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        anonymous_id,
        user_id,
        
            -- case statement solves issue where the url column doesn't include query string parameters.
            case
                when context_page_url ilike '%?%'
                    then context_page_url
                else concat(context_page_url, coalesce(context_page_search, ''))
            end as page_url
            ,
        {{ dbt_utils.get_url_host('context_page_url') }} as page_url_host,
        context_page_path as page_url_path,
        context_page_title as page_title,
        context_page_referrer as referrer,
        
            cast(
                replace( {{ dbt_utils.get_url_host('context_page_referrer') }}, 'www.', '')
                as varchar
            ) as referrer_host
            ,
        context_user_agent as user_agent,
        
            cast(
                case
                    when lower(context_user_agent) like '%android%'
                        then 'Android'
                    else replace(
                        {{ dbt_utils.split_part(dbt_utils.split_part('context_user_agent', "'('", 2), "' '", 1) }},
                    ';',
                    ''
                    )
                end
                as varchar
            ) as device
            ,
        context_ip as ip,
        context_protocols_source_id as segment_protocols_source_id,
        context_protocols_violations as segment_protocols_violations,
        context_protocols_omitted as segment_protocols_omitted_properties,
        code,
        reason,
        reset_code

    from source

)

select * from renamed
