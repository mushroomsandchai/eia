{{ config(materialized = 'table') }}
select 
    extract(year from recorded_date) as year,
    fuel,
    energy_type,
    sum(num_units) as total_generation
from
    {{ ref('dim_generation') }} g
group by
    1, 2, 3
order by 
    2, total_generation desc