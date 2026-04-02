{{ config(
        materialized = 'incremental',
        partition_by = {
            'field': 'recorded_date',
            'data_type': 'date',
            'granularity': 'day',
        },
        unique_key = ['recorded_date', 'recorded_hour', 'provider_id', 'recipient_id'],
        incremental_predicates = [
            "DBT_INTERNAL_DEST.recorded_date >= date_sub(current_date(), interval 7 day)"
        ],
        cluster_by = ['provider_id', 'recipient_id']
) }}
with filtered as (
    select
        recorded_date,
        recorded_hour,
        provider_id,
        recipient_id,
        num_units,
        unit,
        ingestion_time
    from
        {{ ref('stg_interchange') }}
    {% if is_incremental() %}
        {{ get_filter(env_var('WINDOW_DAYS', 7)) }}
    {% endif %}
)
select
    *
from 
    filtered
qualify
    row_number() over(partition by recorded_date, recorded_hour, provider_id, recipient_id order by ingestion_time desc) = 1