{{ config(materialized = 'table') }}
select 
    energy_source_code as fuel_id
    energy_source_name as fuel
from
    {{ ref('energy_sources') }}