{{
  config(
    materialized = 'view',
  )
}}

with

source as (

    select *

    from {{ source('surfline', 'pages') }}

),

renamed as (

    select
        id as page_id,
        'surfline'::varchar as source_schema,
        'pages'::varchar as source_table,
        'surfline-web'::varchar as tracking_plan,
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
        context_campaign_source as utm_source,
        context_campaign_medium as utm_medium,
        context_campaign_name as utm_campaign,
        context_campaign_term as utm_term,
        context_campaign_content as utm_content,
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
        context_locale as locale,
        context_protocols_source_id as segment_protocols_source_id,
        context_protocols_violations as segment_protocols_violations,
        context_protocols_omitted as segment_protocols_omitted_properties,
        ability_levels,
        area_name,
        author,
        author_id,
        author_name,
        board_types,
        buoy_id,
        buoy_name,
        cam_id,
        cam_name,
        cam_name_primary,
        cam_type,
        category,
        category_id,
        category_name,
        channel,
        chart_type,
        cms_id,
        condition,
        content_pillar,
        contest,
        contest_region,
        email,
        forecast_location,
        forecast_name,
        geoname_id,
        geoname_name,
        has_cam,
        human,
        is_instapage,
        is_premium_article,
        is_single_cam,
        is_sponsored_article,
        is_video,
        login_status,
        medium,
        metering_enabled,
        name,
        native,
        path,
        post_categories,
        post_content_pillar,
        post_current_promotion,
        post_date,
        post_id,
        post_series,
        post_tags,
        premium_cam,
        promotion_id,
        referrer,
        region_name,
        search,
        series_id,
        series_name,
        spot_id,
        spot_name,
        sub_category,
        subregion_id,
        subregion_name,
        tag_id,
        tag_name,
        title,
        travel_module_displayed,
        trial_eligible,
        url,
        user_type,
        wave_height_max,
        wave_height_min

    from source

)

select * from renamed
