{{ config(materialized = 'table') }}
select
    recorded_date,
    recorded_hour,
    case
        when demand_type_id = 'DF' then 'Demand Forecast'
        when demand_type_id = 'D' then 'Actual Demand'
        when demand_type_id = 'NG' then 'Net Generation'
    end as demand_type,
    sum(num_units) as value
from
    {{ ref('int_demand_forecast') }}
where
    demand_type_id in ('DF', 'NG', 'D') and
    recorded_date >= current_date() - 30
group by
    1, 2, 3