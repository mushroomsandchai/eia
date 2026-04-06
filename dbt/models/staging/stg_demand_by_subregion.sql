{{ config(materialized = 'view') }}
with renamed as (
    select
        cast(partition_date as date) as recorded_date,
        cast(substr(period, 12, 2) as int64) as recorded_hour,
        cast(subba_name as string) as sub_ba,
        upper(cast(subba as string)) as sub_id,
        cast(parent_name as string) as parent_ba,
        upper(cast(parent as string)) as parent_id,
        coalesce(cast(value as numeric), 0) as num_units,
        cast(value_units as string) as unit,
        cast(ingestion_time as timestamp) as ingestion_time
    from
        {{ source('landing', 'landing_demand_by_subregion') }}
    where 1 = 1
        and period is not null
        and subba is not null
        and parent is not null
        and value_units is not null
        and ingestion_time is not null
        and partition_date is not null
)
select * from renamed