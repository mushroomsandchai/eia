{{ config(materialized = 'table') }}
select
    i.recorded_date,	
    i.provider_id,
    ba.ba_name as provider_name,
    case
        when ba.us_ba = 'Yes' then 'United States of America'
        else ba.region_or_country_name
    end as provider_country,
    i.recipient_id,
    ba2.ba_name as recipient_name,
    case
        when ba2.us_ba = 'Yes' then 'United States of America'
        else ba2.region_or_country_name
    end as recipient_country,
    i.num_units as interchange
from
    {{ ref('int_interchange') }} i
join
    {{ ref('balancing_authorities') }} ba on
    ba.ba_code = i.provider_id
join
    {{ ref('balancing_authorities') }} ba2 on
    ba2.ba_code = i.recipient_id