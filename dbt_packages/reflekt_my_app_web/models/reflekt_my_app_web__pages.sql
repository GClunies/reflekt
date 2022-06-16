{{
  config(
    materialized = 'incremental',
    unique_key = 'page_id',
    cluster_by = 'tstamp'
  )
}}

with

source as (

    select *

    from {{ source('my_app_web', 'pages') }}
    {%- if is_incremental() %}
    where received_at >= ( select max(received_at_tstamp)::date from {{ this }} )
    {%- endif %}

),

renamed as (

    select
        id as page_id,
        'patty_bar_web'::varchar as source_schema,
        'pages'::varchar as source_table,
        'my-plan'::varchar as tracking_plan,
        name as page_name,
        context_library_name as library_name,
        context_library_version as library_version,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        anonymous_id,
        user_id,
        {{ dbt_utils.get_url_host('context_page_url') }} as page_url_host,
        
            cast(
                replace( {{ dbt_utils.get_url_host('context_page_referrer') }}, 'www.', '')
                as varchar
            ) as referrer_host
            ,
        context_ip as ip,
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
        path,
        product_type,
        referrer,
        search,
        title,
        url

    from source

)

select * from renamed
