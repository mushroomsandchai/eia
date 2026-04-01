{{ config(materialized = 'view') }}
with renamed as (
    select
        cast(partition_date as date) as recorded_date,
        cast(substr(period, 12, 2) as int64) as recorded_hour,
        cast(respondent_name as string) as respondent,
        upper(cast(respondent as string)) as respondent_id,
        cast(type_name as string) as demand_type,
        upper(cast(type as string)) as demand_type_id,
        cast(value as numeric) as num_units,
        cast(value_units as string) as unit,
        cast(ingestion_time as timestamp) as ingestion_time
    from
        {{ source('landing', 'landing_demand_forecast') }}
)
select * from renamed