{{ config(materialized = 'table') }}
select 
    g.recorded_date,
    g.recorded_hour,
    g.respondent_id as ba,
    ba.ba_name as name,
    f.fuel,
    g.num_units,
    f.energy_type,
    ba.region_or_country_code,
    case
        when ba.region_or_country_name = 'Canada' then 'Canada'
        when ba.region_or_country_name = 'Mexico' then 'Mexico'
        else 'United States of America'
    end as country

from
    {{ ref('int_generation') }} g
join
    {{ ref('fuel_lookup') }} f on
    f.fuel_id = g.fuel_id
join
    {{ ref('balancing_authorities')}} ba on 
    g.respondent_id = ba.ba_code