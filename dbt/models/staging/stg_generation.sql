{{ config(materialized = 'view') }}
with renamed as (
    select
        cast(partition_date as date) as recorded_date,
        cast(substr(period, 12, 2) as int64) as recorded_hour,
        cast(respondent_name as string) as respondent,
        upper(cast(respondent as string)) as respondent_id,
        cast(type_name as string) as fuel_name,
        upper(cast(fueltype as string)) as fuel_id,
        coalesce(cast(value as numeric), 0) as num_units,
        cast(value_units as string) as unit,
        cast(ingestion_time as timestamp) as ingestion_time
    from
        {{ source('landing', 'landing_generation') }}
    where 1 = 1
        and partition_date is not null
        and period is not null
        and respondent is not null
        and fueltype is not null
        and value_units is not null
        and ingestion_time is not null
)
select * from renamed