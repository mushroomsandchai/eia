def points(start_date, end_date, run_date) -> dict:
    endpoints = [
                    {'type': 'generation','url': 'https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/'},
                    {'type': 'demand_forecast', 'url': 'https://api.eia.gov/v2/electricity/rto/region-data/data/'},
                    {'type': 'demand_by_subregion', 'url': 'https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/'},
                    {'type': 'interchange', 'url': 'https://api.eia.gov/v2/electricity/rto/interchange-data/data/'}
                ]

    for endpoint in endpoints:
        endpoint['directory'] = f"api/{endpoint['type']}/{run_date.year}/{run_date.month:02d}/"
        endpoint['dtobject'] = run_date
        endpoint['start_date'] = start_date
        endpoint['end_date'] = end_date

    return(endpoints)