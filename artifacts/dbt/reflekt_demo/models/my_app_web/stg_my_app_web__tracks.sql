{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select * from {{ source('my_app_web', 'tracks') }}
),

renamed as (
    select
        id,
        original_timestamp as original_tstamp,
        sent_at as sent_at_tstamp,
        received_at as received_at_tstamp,
        timestamp as tstamp,
        type,
        anonymous_id,
        user_id,
        context_active as active,
        context_app_name as app_name,
        context_app_version as app_version,
        context_app_build as app_build,
        context_campaign_name as campaign_name,
        context_campaign_source as campaign_source,
        context_campaign_medium as campaign_medium,
        context_ip as ip,
        context_library_name as library_name,
        context_library_version as library_version,
        context_locale as locale,
        context_location_city as location_city,
        context_location_country as location_country,
        context_location_latitude as location_latitude,
        context_location_longitude as location_longitude,
        context_location_postal_code as location_postal_code,
        context_location_region as location_region,
        context_location_speed as location_speed,
        context_network_bluetooth as network_bluetooth,
        context_network_carrier as network_carrier,
        context_network_cellular as network_cellular,
        context_network_wifi as network_wifi,
        context_os_name as os_name,
        context_os_version as os_version,
        context_page_path as page_path,
        context_page_referrer as page_referrer,
        context_page_search as page_search,
        context_page_title as page_title,
        context_page_url as page_url,
        context_referrer_type as referrer_type,
        context_referrer_name as referrer_name,
        context_referrer_url as referrer_url,
        context_referrer_link as referrer_link,
        context_screen_density as screen_density,
        context_screen_height as screen_height,
        context_screen_width as screen_width,
        context_timezone as timezone,
        context_group_id as group_id,
        context_traits as traits,
        context_user_agent as user_agent,
        version
    from source
)

select * from renamed