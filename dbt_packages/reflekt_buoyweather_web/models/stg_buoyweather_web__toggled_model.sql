{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('buoyweather_web', 'toggled_model') }}

),

renamed as (

    select
        id as event_id,
        'buoyweather'::varchar as source_schema,
        'toggled_model'::varchar as source_table,
        'buoyweather-web'::varchar as tracking_plan,
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
        context_page_search as page_url_query,
        context_page_referrer as referrer,
        
            cast(
                replace( {{ dbt_utils.get_url_host('context_page_referrer') }}, 'www.', '')
                as varchar
            ) as referrer_host
            ,
        context_locale as locale,
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
        lat,
        lon,
        model_name,
        platform

    from source

)

select * from renamed
