# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa
# fmt: off
seg_event_cols = {
    # Common columns
    "id": [
        {
            "source_name": "id",
            "schema_name": "event_id",
            "description": "The unique identifier of the event call.",
            # "tests": ["not_null", "unique"],
            "sql": "id as event_id",
        }
    ],
    "source_schema": [
        {
            "source_name": "source_schema",  # Hack to force this column to be templated
            "schema_name": "source_schema",
            "description": "The schema of the source table.",
            "sql": "'__SCHEMA_NAME__'::varchar as source_schema",
        },
    ],
    "source_table": [
        {
            "source_name": "source_table",  # Hack to force this column to be templated
            "schema_name": "source_table",
            "description": "The source table.",
            "sql": "'__TABLE_NAME__'::varchar as source_table",
        },
    ],
    "tracking_plan": [
        {
            "source_name": "tracking_plan",  # Hack to force this column to be templated
            "schema_name": "tracking_plan",
            "description": "The name of the tracking plan where the event is defined.",
            "sql": "'__PLAN_NAME__'::varchar as tracking_plan",
        },
    ],
    "event_text": [
        {
            "source_name": None,
            "schema_name": "event_name",
            "description": "The name of the event.",
            "sql": "event_text as event_name",
        }
    ],
    "call_type": [
        {
            "source_name": None,
            "schema_name": "call_type",
            "description": "The type of call that generated the data.",
            "sql": "'track'::varchar as call_type",
        }
    ],
    "context_library_name": [
        {
            "source_name": "context_library_name",
            "schema_name": "library_name",
            "description": "Name of the library that invoked the call.",
            "sql": "context_library_name as library_name",
        }
    ],
    "context_library_version": [
        {
            "source_name": "context_library_version",
            "schema_name": "library_version",
            "description": "Version of the library that invoked the call.",
            "sql": "context_library_version as library_version",
        }
    ],
    "original_timestamp": [
        {
            "source_name": "original_timestamp",
            "schema_name": None,
            "description": "Time on the client device when call was invoked, OR the timestamp value manually passed in through server-side libraries.",
            "sql": None,
        }
    ],
    "sent_at": [
        {
            "source_name": "sent_at",
            "schema_name": "sent_at_tstamp",
            "description": "Timestamp when call was sent by client device, OR sent_at value manually passed in. This timestamp can be affected by clock skew on the client device.",
            "sql": "sent_at as sent_at_tstamp",
        }
    ],
    "received_at": [
        {
            "source_name": "received_at",
            "schema_name": "received_at_tstamp",
            "description": "Timestamp when Segment's servers received the call.",
            "sql": "received_at as received_at_tstamp",
        }
    ],
    "timestamp": [
        {
            "source_name": "timestamp",
            "schema_name": "tstamp",
            "description": "Timestamp when the call was invoked. Calculated by Segment to correct client-device clock skew.",
            "sql": 'timestamp as tstamp',
        }
    ],
    "anonymous_id": [
        {
            "source_name": "anonymous_id",
            "schema_name": "anonymous_id",
            "description": "A pseudo-unique substitute for a user ID, for cases when absolute unique identifier not available (e.g. user not signed in).",
            "sql": "anonymous_id",
        }
    ],
    "user_id": [
        {
            "source_name": "user_id",
            "schema_name": "user_id",
            "description": "Unique identifier for the user.",
            "sql": "user_id",
        }
    ],
    # Web columns
    "context_page_url": [
        {
            "source_name": "context_page_url",
            "schema_name": "page_url",
            "description": "The URL of the page where the call was invoked.",
            "sql": "context_page_url as page_url",
        },
        {
            "source_name": None,
            "schema_name": "page_url_host",
            "description": "The hostname of the page where the call was invoked.",
            "sql": "{{ dbt_utils.get_url_host('context_page_url') }} as page_url_host",
        },
    ],
    "context_page_path": [
        {
            "source_name": "context_page_path",
            "schema_name": "page_url_path",
            "description": "The path of the page where the call was invoked.",
            "sql": "context_page_path as page_url_path",
        }
    ],
    "context_page_title": [
        {
            "source_name": "context_page_title",
            "schema_name": "page_title",
            "description": "The title of the page where the call was invoked.",
            "sql": "context_page_title as page_title",
        }
    ],
    "context_page_search": [
        {
            "source_name": "context_page_search",
            "schema_name": "page_url_query",
            "description": "The URL search query parameters of the page where the call was invoked.",
            "sql": "context_page_search as page_url_query",
        }
    ],
    "context_page_referrer": [
        {
            "source_name": "context_page_referrer",
            "schema_name": "referrer",
            "description": "The URL of the page that referred the user to the page where the call was invoked.",
            "sql": "context_page_referrer as page_referrer",
        },
        # {
        #     "source_name": None,
        #     "schema_name": "referrer_host",
        #     "description": "The hostname of the page that referred the user to the page where the call was invoked.",
        #     "sql": """
        #     cast(
        #         replace( {{ dbt_utils.get_url_host('context_page_referrer') }}, 'www.', '')
        #         as varchar
        #     ) as referrer_host
        #     """,
        # },
    ],
    # Mobile columns
    "context_app_name": [
        {
            "source_name": "context_app_name",
            "schema_name": "app_name",
            "description": "The name of the app that invoked the call.",
            "sql": "context_app_name as app_name",
        }
    ],
    "context_app_version": [
        {
            "source_name": "context_app_version",
            "schema_name": "app_version",
            "description": "The version of the app that invoked the call.",
            "sql": "context_app_version as app_version",
        }
    ],
    "context_app_build": [
        {
            "source_name": "context_app_build",
            "schema_name": "app_build",
            "description": "The build of the app that invoked the call.",
            "sql": "context_app_build as app_build",
        }
    ],
    "context_os_name": [
        {
            "source_name": "context_os_name",
            "schema_name": "device_os_name",
            "description": "The operating system on the device.",
            "sql": "context_os_name as device_os_name",
        }
    ],
    "context_os_version": [
        {
            "source_name": "context_os_version",
            "schema_name": "device_os_version",
            "description": "The version of the operating system on the device.",
            "sql": "context_os_version as device_os_version",
        }
    ],
    # Device columns
    "context_locale": [
        {
            "source_name": "context_locale",
            "schema_name": "locale",
            "description": "Locale string for the device generating the event, for example 'en-US'.",
            "sql": "context_locale as locale",
        }
    ],
    "context_user_agent": [  # Web
        {
            "source_name": "context_user_agent",
            "schema_name": "user_agent",
            "description": "The user agent string of the device generating the event.",
            "sql": "context_user_agent as user_agent",
        },
        # {
        #     "source_name": None,
        #     "schema_name": "device",
        #     "description": "The device that invoked the call.",
        #     "sql": """
        #     cast(
        #         case
        #             when lower(context_user_agent) like '%android%'
        #                 then 'Android'
        #             else replace(
        #                 {{ dbt_utils.split_part(dbt_utils.split_part('context_user_agent', "'('", 2), "' '", 1) }},
        #             ';',
        #             ''
        #             )
        #         end
        #         as varchar
        #     ) as device
        #     """,
        # }
    ],
    "context_device_id": [  # Mobile
        {
            "source_name": "context_device_id",
            "schema_name": "device_id",
            "description": "The ID of the device that invoked the call.",
            "sql": "context_device_id as device_id",
        }
    ],
    "context_device_manufacturer": [  # Mobile
        {
            "source_name": "context_device_manufacturer",
            "schema_name": "device_manufacturer",
            "description": "The manufacturer of device that invoked the call.",
            "sql": "context_device_manufacturer as device_manufacturer",
        }
    ],
    "context_device_type": [  # Mobile
        {
            "source_name": "context_device_type",
            "schema_name": "device_type",
            "description": "The type of device that invoked the call.",
            "sql": "context_device_type as device_type",
        }
    ],
    "context_device_model": [  # Mobile
        {
            "source_name": "context_device_model",
            "schema_name": "device",
            "description": "The device that invoked the call.",
            "sql": "context_device_model as device_model",
        },
        # {
        #     "source_name": "context_device_model",
        #     "schema_name": "device",
        #     "description": "The device that invoked the call.",
        #     "sql": "regexp_substr(context_device_model, '[a-zA-Z]+') as device",
        # },
        # {
        #     "source_name": None,
        #     "schema_name": "device_version",
        #     "description": "The version of the device that invoked the call.",
        #     "sql": "regexp_replace(regexp_replace(context_device_model, '[a-zA-Z]', ''), ',', '.') as device_version",
        # },
    ],
    "context_timezone": [  # Mobile
        {
            "source_name": "context_timezone",
            "schema_name": "device_timezone",
            "description": "The timezone of the device that invoked the call.",
            "sql": "context_timezone as device_timezone",
        }
    ],
    "context_screen_height": [  # Mobile
        {
            "source_name": "context_screen_height",
            "schema_name": "screen_height",
            "description": "The height of the device screen in pixels.",
            "sql": "context_screen_height as screen_height",
        }
    ],
    "context_screen_width": [  # Mobile
        {
            "source_name": "context_screen_width",
            "schema_name": "screen_width",
            "description": "The width of the device screen in pixels.",
            "sql": "context_screen_width as screen_width",
        }
    ],
    "context_screen_density": [  # Mobile
        {
            "source_name": "context_screen_density",
            "schema_name": "screen_density",
            "description": "The density of the device screen in pixels per inch.",
            "sql": "context_screen_density as screen_density",
        }
    ],
    # IP and network columns
    "context_ip": [
        {
            "source_name": "context_ip",
            "schema_name": "ip",
            "description": "The IP address the event was generated from.",
            "sql": "context_ip as ip",
        }
    ],
    "context_network_carrier": [
        {
            "source_name": "context_network_carrier",
            "schema_name": "network_carrier",
            "description": "The carrier of the device's network connection.",
            "sql": "context_network_carrier as network_carrier",
        }
    ],
    "context_network_cellular": [
        {
            "source_name": "context_network_cellular",
            "schema_name": "network_cellular",
            "description": "Whether or not the device is connected to a cellular network.",
            "sql": "context_network_cellular as network_cellular",
        }
    ],
    "context_network_wifi": [
        {
            "source_name": "context_network_wifi",
            "schema_name": "network_wifi",
            "description": "Whether or not the device is connected to a wifi network.",
            "sql": "context_network_wifi as network_wifi",
        }
    ],
    "context_network_bluetooth": [
        {
            "source_name": "context_network_bluetooth",
            "schema_name": "network_bluetooth",
            "description": "Whether or not the device is connected to a bluetooth network.",
            "sql": "context_network_bluetooth as network_bluetooth",
        }
    ],
    # Marketing & Ads columns
    "context_campaign_source": [  # Web
        {
            "source_name": "context_campaign_source",
            "schema_name": "utm_source",
            "description": "The source of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_source as utm_source",
        }
    ],
    "context_campaign_medium": [  # Web
        {
            "source_name": "context_campaign_medium",
            "schema_name": "utm_medium",
            "description": "The medium of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_medium as utm_medium",
        }
    ],
    "context_campaign_name": [  # Web
        {
            "source_name": "context_campaign_name",
            "schema_name": "utm_campaign",
            "description": "The name of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_name as utm_campaign",
        }
    ],
    "context_campaign_term": [  # Web
        {
            "source_name": "context_campaign_term",
            "schema_name": "utm_term",
            "description": "The term of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_term as utm_term",
        }
    ],
    "context_campaign_content": [  # Web
        {
            "source_name": "context_campaign_content",
            "schema_name": "utm_content",
            "description": "The content of the campaign that the user was in when the call was invoked. Maps directly to utm_content parameter.",
            "sql": "context_campaign_content as utm_content",
        }
    ],
    "gclid": [  # Web
        {
            "source_name": None,
            "schema_name": "gclid",
            "description": "Google AdWords click ID.",
            "sql": "cast( {{ dbt_utils.get_url_parameter('context_page_url', 'gclid') }} as varchar) as gclid",
        }
    ],
    "fbaid": [  # Web
        {
            "source_name": None,
            "schema_name": "fbaid",
            "description": "Facebook Ad ID.",
            "sql": "cast( {{ dbt_utils.get_url_parameter('context_page_url', 'fbaid') }} as varchar) as fbaid",
        }
    ],
    "context_device_ad_tracking_enabled": [  # Mobile
        {
            "source_name": "context_device_ad_tracking_enabled",
            "schema_name": "ad_tracking_enabled",
            "description": "Whether or not the device has ad tracking enabled for advertising purposes.",
            "sql": "context_device_ad_tracking_enabled as ad_tracking_enabled",
        }
    ],
    "context_device_advertising_id": [  # Mobile
        {
            "source_name": "context_device_advertising_id",
            "schema_name": "advertising_id",
            "description": "The advertising ID of the device that invoked the call.",
            "sql": "context_device_advertising_id as advertising_id",
        }
    ],
    # Segment Protocols columns
    "context_protocols_source_id": [
        {
            "source_name": "context_protocols_source_id",
            "schema_name": "segment_protocols_source_id",
            "description": "If a protocol violation is detected when the call is invoked, the ID of the Segment source.",
            "sql": "context_protocols_source_id as segment_protocols_source_id",
        }
    ],
    "context_protocols_source_name": [
        {
            "source_name": "context_protocols_source_name",
            "schema_name": "segment_protocols_source_name",
            "description": "If a protocol violation is detected when the call is invoked, the name of the Segment source.",
            "sql": "context_protocols_source_name as segment_protocols_source_name",
        }
    ],
    "context_protocols_violations": [
        {
            "source_name": "context_protocols_violations",
            "schema_name": "segment_protocols_violations",
            "description": "A list of Segment Protocols violation (if any) detected when the call was invoked.",
            "sql": "context_protocols_violations as segment_protocols_violations",
        }
    ],
    "context_protocols_omitted": [
        {
            "source_name": "context_protocols_omitted",
            "schema_name": "segment_protocols_omitted_properties",
            "description": "A list of unplanned properties (not in tracking plan) that were omitted by Segment Protocols (i.e. not delivered to destinations).",
            "sql": "context_protocols_omitted as segment_protocols_omitted_properties",
        }
    ],
}

seg_tracks_cols = {
    # Common columns
    "id": [
        {
            "source_name": "id",
            "schema_name": "event_id",
            "description": "The unique identifier of the event call.",
            # "tests": ["not_null", "unique"],
            "sql": "id as event_id",
        }
    ],
    "source_schema": [
        {
            "source_name": "source_schema",  # Hack to force this column to be templated
            "schema_name": "source_schema",
            "description": "The schema of the source table.",
            "sql": "'__SCHEMA_NAME__'::varchar as source_schema",
        },
    ],
    "source_table": [
        {
            "source_name": "source_table",  # Hack to force this column to be templated
            "schema_name": "source_table",
            "description": "The source table.",
            "sql": "'__TABLE_NAME__'::varchar as source_table",
        },
    ],
    "tracking_plan": [
        {
            "source_name": "tracking_plan",  # Hack to force this column to be templated
            "schema_name": "tracking_plan",
            "description": "The name of the tracking plan where the event is defined.",
            "sql": "'__PLAN_NAME__'::varchar as tracking_plan",
        },
    ],
    "event_text": [
        {
            "source_name": "event_name",  # Hack to force this column to be templated
            "schema_name": "event_name",
            "description": "The name of the event.",
            "sql": "event_text as event_name",
        }
    ],
    "call_type": [
        {
            "source_name": None,
            "schema_name": "call_type",
            "description": "The type of call that generated the data.",
            "sql": "'track'::varchar as call_type",
        }
    ],
    "context_library_name": [
        {
            "source_name": "context_library_name",
            "schema_name": "library_name",
            "description": "Name of the library that invoked the call.",
            "sql": "context_library_name as library_name",
        }
    ],
    "context_library_version": [
        {
            "source_name": "context_library_version",
            "schema_name": "library_version",
            "description": "Version of the library that invoked the call.",
            "sql": "context_library_version as library_version",
        }
    ],
    "original_timestamp": [
        {
            "source_name": "original_timestamp",
            "schema_name": None,
            "description": "Time on the client device when call was invoked, OR the timestamp value manually passed in through server-side libraries.",
            "sql": None,
        }
    ],
    "sent_at": [
        {
            "source_name": "sent_at",
            "schema_name": "sent_at_tstamp",
            "description": "Timestamp when call was sent by client device, OR sent_at value manually passed in. This timestamp can be affected by clock skew on the client device.",
            "sql": "sent_at as sent_at_tstamp",
        }
    ],
    "received_at": [
        {
            "source_name": "received_at",
            "schema_name": "received_at_tstamp",
            "description": "Timestamp when Segment's servers received the call.",
            "sql": "received_at as received_at_tstamp",
        }
    ],
    "timestamp": [
        {
            "source_name": "timestamp",
            "schema_name": "tstamp",
            "description": "Timestamp when the call was invoked. Calculated by Segment to correct client-device clock skew.",
            "sql": 'timestamp as tstamp',
        }
    ],
    "anonymous_id": [
        {
            "source_name": "anonymous_id",
            "schema_name": "anonymous_id",
            "description": "A pseudo-unique substitute for a user ID, for cases when absolute unique identifier not available (e.g. user not signed in).",
            "sql": "anonymous_id",
        }
    ],
    "user_id": [
        {
            "source_name": "user_id",
            "schema_name": "user_id",
            "description": "Unique identifier for the user.",
            "sql": "user_id",
        }
    ],
    # Web columns
    "context_page_url": [
        {
            "source_name": "context_page_url",
            "schema_name": "page_url",
            "description": "The URL of the page where the call was invoked.",
            "sql": "context_page_url as page_url",
        },
        {
            "source_name": None,
            "schema_name": "page_url_host",
            "description": "The hostname of the page where the call was invoked.",
            "sql": "{{ dbt_utils.get_url_host('context_page_url') }} as page_url_host",
        },
    ],
    "context_page_path": [
        {
            "source_name": "context_page_path",
            "schema_name": "page_url_path",
            "description": "The path of the page where the call was invoked.",
            "sql": "context_page_path as page_url_path",
        }
    ],
    "context_page_title": [
        {
            "source_name": "context_page_title",
            "schema_name": "page_title",
            "description": "The title of the page where the call was invoked.",
            "sql": "context_page_title as page_title",
        }
    ],
    "context_page_search": [
        {
            "source_name": "context_page_search",
            "schema_name": "page_url_query",
            "description": "The URL search query parameters of the page where the call was invoked.",
            "sql": "context_page_search as page_url_query",
        }
    ],
    "context_page_referrer": [
        {
            "source_name": "context_page_referrer",
            "schema_name": "referrer",
            "description": "The URL of the page that referred the user to the page where the call was invoked.",
            "sql": "context_page_referrer as page_referrer",
        },
        # {
        #     "source_name": None,
        #     "schema_name": "referrer_host",
        #     "description": "The hostname of the page that referred the user to the page where the call was invoked.",
        #     "sql": """
        #     cast(
        #         replace( {{ dbt_utils.get_url_host('context_page_referrer') }}, 'www.', '')
        #         as varchar
        #     ) as referrer_host
        #     """,
        # },
    ],
    # Mobile columns
    "context_app_name": [
        {
            "source_name": "context_app_name",
            "schema_name": "app_name",
            "description": "The name of the app that invoked the call.",
            "sql": "context_app_name as app_name",
        }
    ],
    "context_app_version": [
        {
            "source_name": "context_app_version",
            "schema_name": "app_version",
            "description": "The version of the app that invoked the call.",
            "sql": "context_app_version as app_version",
        }
    ],
    "context_app_build": [
        {
            "source_name": "context_app_build",
            "schema_name": "app_build",
            "description": "The build of the app that invoked the call.",
            "sql": "context_app_build as app_build",
        }
    ],
    "context_os_name": [
        {
            "source_name": "context_os_name",
            "schema_name": "device_os_name",
            "description": "The operating system on the device.",
            "sql": "context_os_name as device_os_name",
        }
    ],
    "context_os_version": [
        {
            "source_name": "context_os_version",
            "schema_name": "device_os_version",
            "description": "The version of the operating system on the device.",
            "sql": "context_os_version as device_os_version",
        }
    ],
    # Device columns
    "context_locale": [
        {
            "source_name": "context_locale",
            "schema_name": "locale",
            "description": "Locale string for the device generating the event, for example 'en-US'.",
            "sql": "context_locale as locale",
        }
    ],
    "context_user_agent": [  # Web
        {
            "source_name": "context_user_agent",
            "schema_name": "user_agent",
            "description": "The user agent string of the device generating the event.",
            "sql": "context_user_agent as user_agent",
        },
        # {
        #     "source_name": None,
        #     "schema_name": "device",
        #     "description": "The device that invoked the call.",
        #     "sql": """
        #     cast(
        #         case
        #             when lower(context_user_agent) like '%android%'
        #                 then 'Android'
        #             else replace(
        #                 {{ dbt_utils.split_part(dbt_utils.split_part('context_user_agent', "'('", 2), "' '", 1) }},
        #             ';',
        #             ''
        #             )
        #         end
        #         as varchar
        #     ) as device
        #     """,
        # }
    ],
    "context_device_id": [  # Mobile
        {
            "source_name": "context_device_id",
            "schema_name": "device_id",
            "description": "The ID of the device that invoked the call.",
            "sql": "context_device_id as device_id",
        }
    ],
    "context_device_manufacturer": [  # Mobile
        {
            "source_name": "context_device_manufacturer",
            "schema_name": "device_manufacturer",
            "description": "The manufacturer of device that invoked the call.",
            "sql": "context_device_manufacturer as device_manufacturer",
        }
    ],
    "context_device_type": [  # Mobile
        {
            "source_name": "context_device_type",
            "schema_name": "device_type",
            "description": "The type of device that invoked the call.",
            "sql": "context_device_type as device_type",
        }
    ],
    "context_device_model": [  # Mobile
        {
            "source_name": "context_device_model",
            "schema_name": "device",
            "description": "The device that invoked the call.",
            "sql": "context_device_model as device_model",
        },
        # {
        #     "source_name": "context_device_model",
        #     "schema_name": "device",
        #     "description": "The device that invoked the call.",
        #     "sql": "regexp_substr(context_device_model, '[a-zA-Z]+') as device",
        # },
        # {
        #     "source_name": None,
        #     "schema_name": "device_version",
        #     "description": "The version of the device that invoked the call.",
        #     "sql": "regexp_replace(regexp_replace(context_device_model, '[a-zA-Z]', ''), ',', '.') as device_version",
        # },
    ],
    "context_timezone": [  # Mobile
        {
            "source_name": "context_timezone",
            "schema_name": "device_timezone",
            "description": "The timezone of the device that invoked the call.",
            "sql": "context_timezone as device_timezone",
        }
    ],
    "context_screen_height": [  # Mobile
        {
            "source_name": "context_screen_height",
            "schema_name": "screen_height",
            "description": "The height of the device screen in pixels.",
            "sql": "context_screen_height as screen_height",
        }
    ],
    "context_screen_width": [  # Mobile
        {
            "source_name": "context_screen_width",
            "schema_name": "screen_width",
            "description": "The width of the device screen in pixels.",
            "sql": "context_screen_width as screen_width",
        }
    ],
    "context_screen_density": [  # Mobile
        {
            "source_name": "context_screen_density",
            "schema_name": "screen_density",
            "description": "The density of the device screen in pixels per inch.",
            "sql": "context_screen_density as screen_density",
        }
    ],
    # IP and network columns
    "context_ip": [
        {
            "source_name": "context_ip",
            "schema_name": "ip",
            "description": "The IP address the event was generated from.",
            "sql": "context_ip as ip",
        }
    ],
    "context_network_carrier": [
        {
            "source_name": "context_network_carrier",
            "schema_name": "network_carrier",
            "description": "The carrier of the device's network connection.",
            "sql": "context_network_carrier as network_carrier",
        }
    ],
    "context_network_cellular": [
        {
            "source_name": "context_network_cellular",
            "schema_name": "network_cellular",
            "description": "Whether or not the device is connected to a cellular network.",
            "sql": "context_network_cellular as network_cellular",
        }
    ],
    "context_network_wifi": [
        {
            "source_name": "context_network_wifi",
            "schema_name": "network_wifi",
            "description": "Whether or not the device is connected to a wifi network.",
            "sql": "context_network_wifi as network_wifi",
        }
    ],
    "context_network_bluetooth": [
        {
            "source_name": "context_network_bluetooth",
            "schema_name": "network_bluetooth",
            "description": "Whether or not the device is connected to a bluetooth network.",
            "sql": "context_network_bluetooth as network_bluetooth",
        }
    ],
    # Marketing & Ads columns
    "context_campaign_source": [  # Web
        {
            "source_name": "context_campaign_source",
            "schema_name": "utm_source",
            "description": "The source of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_source as utm_source",
        }
    ],
    "context_campaign_medium": [  # Web
        {
            "source_name": "context_campaign_medium",
            "schema_name": "utm_medium",
            "description": "The medium of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_medium as utm_medium",
        }
    ],
    "context_campaign_name": [  # Web
        {
            "source_name": "context_campaign_name",
            "schema_name": "utm_campaign",
            "description": "The name of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_name as utm_campaign",
        }
    ],
    "context_campaign_term": [  # Web
        {
            "source_name": "context_campaign_term",
            "schema_name": "utm_term",
            "description": "The term of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_term as utm_term",
        }
    ],
    "context_campaign_content": [  # Web
        {
            "source_name": "context_campaign_content",
            "schema_name": "utm_content",
            "description": "The content of the campaign that the user was in when the call was invoked. Maps directly to utm_content parameter.",
            "sql": "context_campaign_content as utm_content",
        }
    ],
    "gclid": [  # Web
        {
            "source_name": None,
            "schema_name": "gclid",
            "description": "Google AdWords click ID.",
            "sql": "cast( {{ dbt_utils.get_url_parameter('context_page_url', 'gclid') }} as varchar) as gclid",
        }
    ],
    "fbaid": [  # Web
        {
            "source_name": None,
            "schema_name": "fbaid",
            "description": "Facebook Ad ID.",
            "sql": "cast( {{ dbt_utils.get_url_parameter('context_page_url', 'fbaid') }} as varchar) as fbaid",
        }
    ],
    "context_device_ad_tracking_enabled": [  # Mobile
        {
            "source_name": "context_device_ad_tracking_enabled",
            "schema_name": "ad_tracking_enabled",
            "description": "Whether or not the device has ad tracking enabled for advertising purposes.",
            "sql": "context_device_ad_tracking_enabled as ad_tracking_enabled",
        }
    ],
    "context_device_advertising_id": [  # Mobile
        {
            "source_name": "context_device_advertising_id",
            "schema_name": "advertising_id",
            "description": "The advertising ID of the device that invoked the call.",
            "sql": "context_device_advertising_id as advertising_id",
        }
    ],
    # Segment Protocols columns
    "context_protocols_source_id": [
        {
            "source_name": "context_protocols_source_id",
            "schema_name": "segment_protocols_source_id",
            "description": "If a protocol violation is detected when the call is invoked, the ID of the Segment source.",
            "sql": "context_protocols_source_id as segment_protocols_source_id",
        }
    ],
    "context_protocols_source_name": [
        {
            "source_name": "context_protocols_source_name",
            "schema_name": "segment_protocols_source_name",
            "description": "If a protocol violation is detected when the call is invoked, the name of the Segment source.",
            "sql": "context_protocols_source_name as segment_protocols_source_name",
        }
    ],
    "context_protocols_violations": [
        {
            "source_name": "context_protocols_violations",
            "schema_name": "segment_protocols_violations",
            "description": "A list of Segment Protocols violation (if any) detected when the call was invoked.",
            "sql": "context_protocols_violations as segment_protocols_violations",
        }
    ],
    "context_protocols_omitted": [
        {
            "source_name": "context_protocols_omitted",
            "schema_name": "segment_protocols_omitted_properties",
            "description": "A list of unplanned properties (not in tracking plan) that were omitted by Segment Protocols (i.e. not delivered to destinations).",
            "sql": "context_protocols_omitted as segment_protocols_omitted_properties",
        }
    ],
}

seg_pages_cols = {
    "id": [
        {
            "source_name": "id",
            "schema_name": "page_id",
            "description": "The unique identifier of the page call.",
            # "tests": ["not_null", "unique"],
            "sql": "id as page_id",
        }
    ],
    "source_schema": [
        {
            "source_name": "source_schema",  # Hack to force this column to be templated
            "schema_name": "source_schema",
            "description": "The schema of the source table.",
            "sql": "'__SCHEMA_NAME__'::varchar as source_schema",
        },
    ],
    "source_table": [
        {
            "source_name": "source_table",  # Hack to force this column to be templated
            "schema_name": "source_table",
            "description": "The source table.",
            "sql": "'__TABLE_NAME__'::varchar as source_table",
        },
    ],
    "tracking_plan": [
        {
            "source_name": "tracking_plan",  # Hack to force this column to be templated
            "schema_name": "tracking_plan",
            "description": "The name of the tracking plan where the event is defined.",
            "sql": "'__PLAN_NAME__'::varchar as tracking_plan",
        },
    ],
    "name": [
        {
            "source_name": "name",
            "schema_name": "page_name",
            "description": "The page name (used to group similar pages, e.g., `Spot Report`).",
            "sql": "name as page_name",
        }
    ],
    "call_type": [
        {
            "source_name": None,
            "schema_name": "call_type",
            "description": "The type of call that generated the data.",
            "sql": "'page'::varchar as call_type",
        }
    ],
    "context_library_name": [
        {
            "source_name": "context_library_name",
            "schema_name": "library_name",
            "description": "The name of the library that invoked the call.",
            "sql": "context_library_name as library_name",
        }
    ],
    "context_library_version": [
        {
            "source_name": "context_library_version",
            "schema_name": "library_version",
            "description": "The version of the library that invoked the call.",
            "sql": "context_library_version as library_version",
        }
    ],
    "original_timestamp": [
        {
            "source_name": "original_timestamp",
            "schema_name": None,
            "description": "Time on the client device when call was invoked, OR the timestamp value manually passed in through server-side libraries.",
            "sql": None,
        }
    ],
    "sent_at": [
        {
            "source_name": "sent_at",
            "schema_name": "sent_at_tstamp",
            "description": "Time on client device when call was sent, OR sent_at value manually passed in. NOTE - sent_at is NOT USEFUL for analysis since it’s not always trustworthy as it can be easily adjusted and affected by clock skew.",
            "sql": "sent_at as sent_at_tstamp",
        }
    ],
    "received_at": [
        {
            "source_name": "received_at",
            "schema_name": "received_at_tstamp",
            "description": "Time on Segment server clock when call was received. received_at is used as sort key in Warehouses. For max query speed, received_at is the recommended timestamp for analysis when chronology DOES NOT matter as chronology is NOT ENSURED.",
            "sql": "received_at as received_at_tstamp",
        }
    ],
    "timestamp": [
        {
            "source_name": "timestamp",
            "schema_name": "tstamp",
            "description": "When the call was invoked. Calculated by Segment to correct client-device clock skew. Use for analysis when chronology DOES matter.",
            "sql": 'timestamp as tstamp',
        }
    ],
    "anonymous_id": [
        {
            "source_name": "anonymous_id",
            "schema_name": "anonymous_id",
            "description": "A pseudo-unique substitute for a user ID, for cases when we don’t have an absolutely unique identifier. A user_id or an anonymous_id is required for all events.",
            "sql": "anonymous_id",
        }
    ],
    "user_id": [
        {
            "source_name": "user_id",
            "schema_name": "user_id",
            "description": "Unique identifier for the user. A user_id or an anonymous_id is required for all events.",
            "sql": "user_id",
        }
    ],
    "context_page_url": [
        {
            "source_name": "context_page_url",
            "schema_name": "page_url",
            "description": "The URL of the page where the call was invoked.",
            "sql": "context_page_url as page_url",
        },
        {
            "source_name": None,
            "schema_name": "page_url_host",
            "description": "The hostname of the page where the call was invoked.",
            "sql": "{{ dbt_utils.get_url_host('context_page_url') }} as page_url_host",
        },
    ],
    "context_page_path": [
        {
            "source_name": "context_page_path",
            "schema_name": "page_url_path",
            "description": "The path of the page where the call was invoked.",
            "sql": "context_page_path as page_url_path",
        }
    ],
    "context_page_title": [
        {
            "source_name": "context_page_title",
            "schema_name": "page_title",
            "description": "The title of the page where the call was invoked.",
            "sql": "context_page_title as page_title",
        }
    ],
    "context_page_search": [
        {
            "source_name": "context_page_search",
            "schema_name": "page_url_query",
            "description": "The URL search query parameters of the page where the call was invoked.",
            "sql": "context_page_search as page_url_query",
        }
    ],
    "context_page_referrer": [
        {
            "source_name": "context_page_referrer",
            "schema_name": "referrer",
            "description": "The URL of the page that referred the user to the page where the call was invoked.",
            "sql": "context_page_referrer as page_referrer",
        },
        {
            "source_name": None,
            "schema_name": "referrer_host",
            "description": "The hostname of the page that referred the user to the page where the call was invoked.",
            "sql": """
            cast(
                replace( {{ dbt_utils.get_url_host('context_page_referrer') }}, 'www.', '')
                as varchar
            ) as referrer_host
            """,
        },
    ],
    "context_campaign_source": [
        {
            "source_name": "context_campaign_source",
            "schema_name": "utm_source",
            "description": "The source of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_source as utm_source",
        }
    ],
    "context_campaign_medium": [
        {
            "source_name": "context_campaign_medium",
            "schema_name": "utm_medium",
            "description": "The medium of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_medium as utm_medium",
        }
    ],
    "context_campaign_name": [
        {
            "source_name": "context_campaign_name",
            "schema_name": "utm_campaign",
            "description": "The name of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_name as utm_campaign",
        }
    ],
    "context_campaign_term": [
        {
            "source_name": "context_campaign_term",
            "schema_name": "utm_term",
            "description": "The term of the campaign that the user was in when the call was invoked.",
            "sql": "context_campaign_term as utm_term",
        }
    ],
    "context_campaign_content": [
        {
            "source_name": "context_campaign_content",
            "schema_name": "utm_content",
            "description": "The content of the campaign that the user was in when the call was invoked. Maps directly to utm_content parameter.",
            "sql": "context_campaign_content as utm_content",
        }
    ],
    "gclid": [
        {
            "source_name": None,
            "schema_name": "gclid",
            "description": "Google AdWords click ID.",
            "sql": "cast( {{ dbt_utils.get_url_parameter('context_page_url', 'gclid') }} as varchar) as gclid",
        }
    ],
    "fbaid": [
        {
            "source_name": None,
            "schema_name": "fbaid",
            "description": "Facebook Ad ID.",
            "sql": "cast( {{ dbt_utils.get_url_parameter('context_page_url', 'fbaid') }} as varchar) as fbaid",
        }
    ],
    "context_ip": [
        {
            "source_name": "context_ip",
            "schema_name": "ip",
            "description": "The IP address the event was generated from.",
            "sql": "context_ip as ip",
        }
    ],
    "context_user_agent": [
        {
            "source_name": "context_user_agent",
            "schema_name": "user_agent",
            "description": "The user agent string of the device generating the event.",
            "sql": "context_user_agent as user_agent",
        },
        # {
        #     "source_name": None,
        #     "schema_name": "device",
        #     "description": "The device that invoked the call.",
        #     "sql": """
        #     cast(
        #         case
        #             when lower(context_user_agent) like '%android%'
        #                 then 'Android'
        #             else replace(
        #                 {{ dbt_utils.split_part(dbt_utils.split_part('context_user_agent', "'('", 2), "' '", 1) }},
        #             ';',
        #             ''
        #             )
        #         end
        #         as varchar
        #     ) as device
        #     """,
        # }
    ],
    "context_locale": [
        {
            "source_name": "context_locale",
            "schema_name": "locale",
            "description": "Locale string for the device generating the event, for example 'en-US'.",
            "sql": "context_locale as locale",
        }
    ],
    "context_protocols_source_id": [
        {
            "source_name": "context_protocols_source_id",
            "schema_name": "segment_protocols_source_id",
            "description": "If a protocol violation is detected when the call is invoked, the ID of the Segment source.",
            "sql": "context_protocols_source_id as segment_protocols_source_id",
        }
    ],
    "context_protocols_source_name": [
        {
            "source_name": "context_protocols_source_name",
            "schema_name": "segment_protocols_source_name",
            "description": "If a protocol violation is detected when the call is invoked, the name of the Segment source.",
            "sql": "context_protocols_source_name as segment_protocols_source_name",
        }
    ],
    "context_protocols_violations": [
        {
            "source_name": "context_protocols_violations",
            "schema_name": "segment_protocols_violations",
            "description": "A list of Segment Protocols violation (if any) detected when the call was invoked.",
            "sql": "context_protocols_violations as segment_protocols_violations",
        }
    ],
    "context_protocols_omitted": [
        {
            "source_name": "context_protocols_omitted",
            "schema_name": "segment_protocols_omitted_properties",
            "description": "A list of unplanned properties (not in tracking plan) that were omitted by Segment Protocols (i.e. not delivered to destinations).",
            "sql": "context_protocols_omitted as segment_protocols_omitted_properties",
        }
    ],
}

seg_screens_cols = {
    "id": [
        {
            "source_name": "id",
            "schema_name": "screen_id",
            "description": "The unique identifier of the screen call.",
            # "tests": ["not_null", "unique"],
            "sql": "id as screen_id",
        }
    ],
    "source_schema": [
        {
            "source_name": "source_schema",  # Hack to force this column to be templated
            "schema_name": "source_schema",
            "description": "The schema of the source table.",
            "sql": "'__SCHEMA_NAME__'::varchar as source_schema",
        },
    ],
    "source_table": [
        {
            "source_name": "source_table",  # Hack to force this column to be templated
            "schema_name": "source_table",
            "description": "The source table.",
            "sql": "'__TABLE_NAME__'::varchar as source_table",
        },
    ],
    "tracking_plan": [
        {
            "source_name": "tracking_plan",  # Hack to force this column to be templated
            "schema_name": "tracking_plan",
            "description": "The name of the tracking plan where the event is defined.",
            "sql": "'__PLAN_NAME__'::varchar as tracking_plan",
        },
    ],
    "name": [
        {
            "source_name": "name",
            "schema_name": "screen_name",
            "description": "The screen name (used to group similar pages, e.g., `Spot`).",
            "sql": "name as screen_name",
        }
    ],
    "call_type": [
        {
            "source_name": None,
            "schema_name": "call_type",
            "description": "The type of call that generated the data.",
            "sql": "'screen'::varchar as call_type",
        }
    ],
    "context_library_name": [
        {
            "source_name": "context_library_name",
            "schema_name": "library_name",
            "description": "The name of the library that invoked the call.",
            "sql": "context_library_name as library_name",
        }
    ],
    "context_library_version": [
        {
            "source_name": "context_library_version",
            "schema_name": "library_version",
            "description": "The version of the library that invoked the call.",
            "sql": "context_library_version as library_version",
        }
    ],
    "original_timestamp": [
        {
            "source_name": "original_timestamp",
            "schema_name": None,
            "description": "Time on the client device when call was invoked, OR the timestamp value manually passed in through server-side libraries.",
            "sql": None,
        }
    ],
    "sent_at": [
        {
            "source_name": "sent_at",
            "schema_name": "sent_at_tstamp",
            "description": "Time on client device when call was sent, OR sent_at value manually passed in. NOTE - sent_at is NOT USEFUL for analysis since it’s not always trustworthy as it can be easily adjusted and affected by clock skew.",
            "sql": "sent_at as sent_at_tstamp",
        }
    ],
    "received_at": [
        {
            "source_name": "received_at",
            "schema_name": "received_at_tstamp",
            "description": "Time on Segment server clock when call was received. received_at is used as sort key in Warehouses. For max query speed, received_at is the recommended timestamp for analysis when chronology DOES NOT matter as chronology is NOT ENSURED.",
            "sql": "received_at as received_at_tstamp",
        }
    ],
    "timestamp": [
        {
            "source_name": "timestamp",
            "schema_name": "tstamp",
            "description": "When the call was invoked. Calculated by Segment to correct client-device clock skew. Use for analysis when chronology DOES matter.",
            "sql": 'timestamp as tstamp',
        }
    ],
    "anonymous_id": [
        {
            "source_name": "anonymous_id",
            "schema_name": "anonymous_id",
            "description": "A pseudo-unique substitute for a user ID, for cases when we don’t have an absolutely unique identifier. A user_id or an anonymous_id is required for all events.",
            "sql": "anonymous_id",
        }
    ],
    "user_id": [
        {
            "source_name": "user_id",
            "schema_name": "user_id",
            "description": "Unique identifier for the user. A user_id or an anonymous_id is required for all events.",
            "sql": "user_id",
        }
    ],
    "context_app_name": [
        {
            "source_name": "context_app_name",
            "schema_name": "app_name",
            "description": "The name of the app that invoked the call.",
            "sql": "context_app_name as app_name",
        }
    ],
    "context_app_version": [
        {
            "source_name": "context_app_version",
            "schema_name": "app_version",
            "description": "The version of the app that invoked the call.",
            "sql": "context_app_version as app_version",
        }
    ],
    "context_app_build": [
        {
            "source_name": "context_app_build",
            "schema_name": "app_build",
            "description": "The build of the app that invoked the call.",
            "sql": "context_app_build as app_build",
        }
    ],
    "context_os_name": [
        {
            "source_name": "context_os_name",
            "schema_name": "device_os_name",
            "description": "The operating system on the device.",
            "sql": "context_os_name as device_os_name",
        }
    ],
    "context_os_version": [
        {
            "source_name": "context_os_version",
            "schema_name": "device_os_version",
            "description": "The version of the operating system on the device.",
            "sql": "context_os_version as device_os_version",
        }
    ],
    "context_device_id": [
        {
            "source_name": "context_device_id",
            "schema_name": "device_id",
            "description": "The ID of the device that invoked the call.",
            "sql": "context_device_id as device_id",
        }
    ],
    "context_device_manufacturer": [
        {
            "source_name": "context_device_manufacturer",
            "schema_name": "device_manufacturer",
            "description": "The manufacturer of device that invoked the call.",
            "sql": "context_device_manufacturer as device_manufacturer",
        }
    ],
    "context_device_type": [
        {
            "source_name": "context_device_type",
            "schema_name": "device_type",
            "description": "The type of device that invoked the call.",
            "sql": "context_device_type as device_type",
        }
    ],
    "context_device_model": [
        {
            "source_name": "context_device_model",
            "schema_name": "device",
            "description": "The device that invoked the call.",
            "sql": "context_device_model as device_model",
        },
        # {
        #     "source_name": "context_device_model",
        #     "schema_name": "device",
        #     "description": "The device that invoked the call.",
        #     "sql": "regexp_substr(context_device_model, '[a-zA-Z]+') as device",
        # },
        # {
        #     "source_name": None,
        #     "schema_name": "device_version",
        #     "description": "The version of the device that invoked the call.",
        #     "sql": "regexp_replace(regexp_replace(context_device_model, '[a-zA-Z]', ''), ',', '.') as device_version",
        # },
    ],
    "context_timezone": [
        {
            "source_name": "context_timezone",
            "schema_name": "device_timezone",
            "description": "The timezone of the device that invoked the call.",
            "sql": "context_timezone as device_timezone",
        }
    ],
    "context_screen_height": [
        {
            "source_name": "context_screen_height",
            "schema_name": "screen_height",
            "description": "The height of the device screen in pixels.",
            "sql": "context_screen_height as screen_height",
        }
    ],
    "context_screen_width": [
        {
            "source_name": "context_screen_width",
            "schema_name": "screen_width",
            "description": "The width of the device screen in pixels.",
            "sql": "context_screen_width as screen_width",
        }
    ],
    "context_screen_density": [
        {
            "source_name": "context_screen_density",
            "schema_name": "screen_density",
            "description": "The density of the device screen in pixels per inch.",
            "sql": "context_screen_density as screen_density",
        }
    ],
    "context_ip": [
        {
            "source_name": "context_ip",
            "schema_name": "ip",
            "description": "The IP address the event was generated from.",
            "sql": "context_ip as ip",
        }
    ],
    "context_locale": [
        {
            "source_name": "context_locale",
            "schema_name": "locale",
            "description": "Locale string for the device generating the event, for example 'en-US'.",
            "sql": "context_locale as locale",
        }
    ],
    "context_network_carrier": [
        {
            "source_name": "context_network_carrier",
            "schema_name": "network_carrier",
            "description": "The carrier of the device's network connection.",
            "sql": "context_network_carrier as network_carrier",
        }
    ],
    "context_network_cellular": [
        {
            "source_name": "context_network_cellular",
            "schema_name": "network_cellular",
            "description": "Whether or not the device is connected to a cellular network.",
            "sql": "context_network_cellular as network_cellular",
        }
    ],
    "context_network_wifi": [
        {
            "source_name": "context_network_wifi",
            "schema_name": "network_wifi",
            "description": "Whether or not the device is connected to a wifi network.",
            "sql": "context_network_wifi as network_wifi",
        }
    ],
    "context_network_bluetooth": [
        {
            "source_name": "context_network_bluetooth",
            "schema_name": "network_bluetooth",
            "description": "Whether or not the device is connected to a bluetooth network.",
            "sql": "context_network_bluetooth as network_bluetooth",
        }
    ],
    "context_device_ad_tracking_enabled": [
        {
            "source_name": "context_device_ad_tracking_enabled",
            "schema_name": "ad_tracking_enabled",
            "description": "Whether or not the device has ad tracking enabled for advertising purposes.",
            "sql": "context_device_ad_tracking_enabled as ad_tracking_enabled",
        }
    ],
    "context_device_advertising_id": [
        {
            "source_name": "context_device_advertising_id",
            "schema_name": "advertising_id",
            "description": "The advertising ID of the device that invoked the call.",
            "sql": "context_device_advertising_id as advertising_id",
        }
    ],
    "context_protocols_source_id": [
        {
            "source_name": "context_protocols_source_id",
            "schema_name": "segment_protocols_source_id",
            "description": "If a protocol violation is detected when the call is invoked, the ID of the Segment source.",
            "sql": "context_protocols_source_id as segment_protocols_source_id",
        }
    ],
    "context_protocols_source_name": [
        {
            "source_name": "context_protocols_source_name",
            "schema_name": "segment_protocols_source_name",
            "description": "If a protocol violation is detected when the call is invoked, the name of the Segment source.",
            "sql": "context_protocols_source_name as segment_protocols_source_name",
        }
    ],
    "context_protocols_violations": [
        {
            "source_name": "context_protocols_violations",
            "schema_name": "segment_protocols_violations",
            "description": "A list of Segment Protocols violation (if any) detected when the call was invoked.",
            "sql": "context_protocols_violations as segment_protocols_violations",
        }
    ],
    "context_protocols_omitted": [
        {
            "source_name": "context_protocols_omitted",
            "schema_name": "segment_protocols_omitted_properties",
            "description": "A list of unplanned properties (not in tracking plan) that were omitted by Segment Protocols (i.e. not delivered to destinations).",
            "sql": "context_protocols_omitted as segment_protocols_omitted_properties",
        }
    ],
}

seg_identify_cols = {
    "id": [
        {
            "source_name": "id",
            "schema_name": "identify_id",
            "description": "The unique identifier of the identify call.",
            # "tests": ["not_null", "unique"],
            "sql": "id as identify_id",
        }
    ],
    "source_schema": [
        {
            "source_name": "source_schema",  # Hack to force this column to be templated
            "schema_name": "source_schema",
            "description": "The schema of the source table.",
            "sql": "'__SCHEMA_NAME__'::varchar as source_schema",
        },
    ],
    "source_table": [
        {
            "source_name": "source_table",  # Hack to force this column to be templated
            "schema_name": "source_table",
            "description": "The source table.",
            "sql": "'__TABLE_NAME__'::varchar as source_table",
        },
    ],
    "tracking_plan": [
        {
            "source_name": "tracking_plan",  # Hack to force this column to be templated
            "schema_name": "tracking_plan",
            "description": "The name of the tracking plan where the event is defined.",
            "sql": "'__PLAN_NAME__'::varchar as tracking_plan",
        },
    ],
    "call_type": [
        {
            "source_name": None,
            "schema_name": "call_type",
            "description": "The type of call that generated the data.",
            "sql": "'identify'::varchar as call_type",
        }
    ],
    "received_at": [
        {
            "source_name": "received_at",
            "schema_name": "received_at_tstamp",
            "description": "The timestamp when the identify call hit Segment's API.",
            "sql": "received_at as received_at_tstamp",
        },
    ],
    "sent_at": [
        {
            "source_name": "sent_at",
            "schema_name": "sent_at_tstamp",
            "description": "The timestamp when the client’s device made the network request to the Segment API.",
            "sql": "sent_at as sent_at_tstamp",
        },
    ],
    "timestamp": [
        {
            "source_name": "timestamp",
            "schema_name": "tstamp",
            "description": "When the call was invoked. Calculated by Segment to correct client-device clock skew. Use for analysis when chronology DOES matter.",
            "sql": '"timestamp" as tstamp',
        },
    ],
    "anonymous_id": [
        {
            "source_name": "anonymous_id",
            "schema_name": "anonymous_id",
            "description": "A pseudo-unique substitute for a User ID, for cases when we don’t have an absolutely unique identifier.",
            "sql": "anonymous_id",
        },
    ],
    "user_id": [
        {
            "source_name": "user_id",
            "schema_name": "user_id",
            "description": "Unique identifier for the user.",
            "sql": "user_id",
        },
    ],
}

seg_users_cols = {
    "id": [
        {
            "source_name": "id",
            "schema_name": "user_id",
            "description": "The unique identifier of the user.",
            # "tests": ["not_null", "unique"],
            "sql": "id as user_id",
        },
    ],
    "source_schema": [
        {
            "source_name": "source_schema",  # Hack to force this column to be templated
            "schema_name": "source_schema",
            "description": "The schema of the source table.",
            "sql": "'__SCHEMA_NAME__'::varchar as source_schema",
        },
    ],
    "source_table": [
        {
            "source_name": "source_table",  # Hack to force this column to be templated
            "schema_name": "source_table",
            "description": "The source table.",
            "sql": "'__TABLE_NAME__'::varchar as source_table",
        },
    ],
    "tracking_plan": [
        {
            "source_name": "tracking_plan",  # Hack to force this column to be templated
            "schema_name": "tracking_plan",
            "description": "The name of the tracking plan where the event is defined.",
            "sql": "'__PLAN_NAME__'::varchar as tracking_plan",
        },
    ],
    "received_at": [
        {
            "source_name": "received_at",
            "schema_name": "received_at_tstamp",
            "description": "The timestamp when the identify call hit Segment's API.",
            "sql": "received_at as received_at_tstamp",
        },
    ],
    "sent_at": [
        {
            "source_name": "sent_at",
            "schema_name": "sent_at_tstamp",
            "description": "The timestamp when the client’s device made the network request to the Segment API.",
            "sql": "sent_at as sent_at_tstamp",
        },
    ],
    "timestamp": [
        {
            "source_name": "timestamp",
            "schema_name": "tstamp",
            "description": "When the call was invoked. Calculated by Segment to correct client-device clock skew. Use for analysis when chronology DOES matter.",
            "sql": '"timestamp" as tstamp',
        },
    ],
    # "anonymous_id": [
    #     {
    #         "source_name": "anonymous_id",
    #         "schema_name": "anonymous_id",
    #         "description": "A pseudo-unique substitute for a User ID, for cases when we don’t have an absolutely unique identifier.",
    #         "sql": "anonymous_id",
    #     },
    # ],
    # "user_id": [
    #     {
    #         "source_name": "user_id",
    #         "schema_name": "user_id",
    #         "description": "Unique identifier for the user.",
    #         "sql": "user_id",
    #     },
    # ],
}

seg_groups_cols = {
    "group_id": [
        {
            "source_name": "id",
            "schema_name": "group_id",
            "description": "The unique identifier of the group.",
            # "tests": ["not_null", "unique"],
            "sql": "id as group_id",
        },
    ],
    "source_schema": [
        {
            "source_name": "source_schema",  # Hack to force this column to be templated
            "schema_name": "source_schema",
            "description": "The schema of the source table.",
            "sql": "'__SCHEMA_NAME__'::varchar as source_schema",
        },
    ],
    "source_table": [
        {
            "source_name": "source_table",  # Hack to force this column to be templated
            "schema_name": "source_table",
            "description": "The source table.",
            "sql": "'__TABLE_NAME__'::varchar as source_table",
        },
    ],
    "tracking_plan": [
        {
            "source_name": "tracking_plan",  # Hack to force this column to be templated
            "schema_name": "tracking_plan",
            "description": "The name of the tracking plan where the event is defined.",
            "sql": "'__PLAN_NAME__'::varchar as tracking_plan",
        },
    ],
    "call_type": [
        {
            "source_name": None,
            "schema_name": "call_type",
            "description": "The type of call that generated the data.",
            "sql": "'group'::varchar as call_type",
        }
    ],
    "received_at": [
        {
            "source_name": "received_at",
            "schema_name": "received_at_tstamp",
            "description": "The timestamp when the identify call hit Segment's API.",
            "sql": "received_at as received_at_tstamp",
        },
    ],
    "sent_at": [
        {
            "source_name": "sent_at",
            "schema_name": "sent_at_tstamp",
            "description": "The timestamp when the client’s device made the network request to the Segment API.",
            "sql": "sent_at as sent_at_tstamp",
        },
    ],
    "timestamp": [
        {
            "source_name": "timestamp",
            "schema_name": "tstamp",
            "description": "When the call was invoked. Calculated by Segment to correct client-device clock skew. Use timestamp for analysis when chronology DOES matter.",
            "sql": '"timestamp" as tstamp',
        },
    ],
    # "anonymous_id": [
    #     {
    #         "source_name": "anonymous_id",
    #         "schema_name": "anonymous_id",
    #         "description": "A pseudo-unique substitute for a User ID, for cases when we don’t have an absolutely unique identifier.",
    #         "sql": "anonymous_id",
    #     },
    # ],
    # "group_id": [
    #     {
    #         "source_name": "group_id",
    #         "schema_name": "group_id",
    #         "description": "Unique identifier for the group.",
    #         "sql": "group_id",
    #     },
    # ],
}
