{{ config(materialized = 'view') }}
select 
    energy_source_code as fuel_id,
    energy_source_name as fuel,
    case
        when energy_source_name in (
            'Wind',
            'Solar',
            'Hydro and pumped storage',
            'Geothermal',
            'Wind with integrated battery storage',
            'Solar with integrated battery storage',
            'Battery storage',
            'Pumped storage',
            'Nuclear'
        ) then 'renewable'
        else 'non-renewable'
    end as energy_type
from
    {{ ref('energy_sources') }}