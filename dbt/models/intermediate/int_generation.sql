{{ 
    config(
        materialized = 'incremental',
        partition_by = {
            'field' = 'recorded_date',
            'data_type' = 'date',
            'granularity' = 'day',
        },
        cluster_by = ['respondent_id', 'fuel_id']
) }}
with filtered as (
    select
        recorded_date,
        recorded_hour,
        respondent_id,
        fuel_id,
        num_units,
        unit,
        ingestion_time
    from
        {{ ref('stg_generation') }}
    {% if is_incremental() %}
        where
            recorded_date >= current_date - {{ env_var('WINDOW_DAYS', 7) }}
    {% endif %}
)
select
    *
from 
    filtered
qualify
    row_number() over(partition by recorded_date, recorded_hour, respondent_id, fuel_id order by ingestion_time desc) = 1