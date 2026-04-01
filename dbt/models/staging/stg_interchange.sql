{{ config(materialized = 'view') }}
with renamed as (
    select
        cast(partition_date as date) as recorded_date,
        cast(substr(period, 12, 2) as int64) as recorded_hour,
        cast(fromba_name as string) as provider_ba,
        upper(cast(fromba as string)) as provider_ba_id,
        cast(toba_name as string) as recipient_ba,
        upper(cast(toba as string)) as recipient_ba_id,
        coalesce(cast(value as numeric), 0) as num_units,
        cast(value_units as string) as unit,
        cast(ingestion_time as timestamp) as ingestion_time
    from
        {{ source('landing', 'landing_interchange') }}
)
select * from renamed