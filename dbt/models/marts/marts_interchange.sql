{{ config(materialized = 'table') }}
select    
    recorded_date,
    provider_country,
    recipient_country,
    sum(interchange) as interchange
from
    {{ ref('dim_interchange') }}
where
    provider_country != recipient_country
group by 
    1, 2, 3