{{
  config(
    materialized = 'view'
  )
}}

with

source as (
    select *
    from {{ source('cli_dev_segment', 'schemas_pulled') }}
    where received_at < get_date()
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
        context_app_name as app_name,
        context_app_version as app_version,
        context_library_name as library_name,
        context_library_version as library_version,
        context_protocols_source_id as protocols_source_id,
        ci,
        count_schemas,
        profile_id,
        project_id,
        schema_registry,
        'track'::varchar as call_type,
        'cli_dev_segment'::varchar as source_schema,
        'schemas_pulled'::varchar as source_table,
        'segment/reflekt_cli/Schemas_Pulled/1-0.json'::varchar as schema_id
    from source
)

select * from renamed