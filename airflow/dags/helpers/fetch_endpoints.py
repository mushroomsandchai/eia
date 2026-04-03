import os
from datetime import datetime, timedelta

def points(logical_date, type = None) -> dict:
    endpoints = [
                    {'type': 'generation','url': 'https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/'},
                    {'type': 'demand_forecast', 'url': 'https://api.eia.gov/v2/electricity/rto/region-data/data/'},
                    {'type': 'demand_by_subregion', 'url': 'https://api.eia.gov/v2/electricity/rto/region-sub-ba-data/data/'},
                    {'type': 'interchange', 'url': 'https://api.eia.gov/v2/electricity/rto/interchange-data/data/'}
                ]

    for endpoint in endpoints:

        if type != 'monthly':
            if endpoint['type'] != 'demand_forecast':
                run_date = logical_date - timedelta(days = 1)
            else:
                run_date = logical_date

            endpoint['dtobject'] = run_date
            endpoint['directory'] = f"api/{endpoint['type']}/{run_date.year}/{run_date.month:02d}/"
            
            if type == 'refresh':
                window = int(os.environ.get('WINDOW_DAYS', 7))
                endpoint['start_date'] = (run_date - timedelta(days = window)).strftime('%Y-%m-%dT00')
                endpoint['end_date'] = run_date.strftime('%Y-%m-%dT23')
            else:
                endpoint['start_date'] = run_date.strftime('%Y-%m-%dT00')
                endpoint['end_date'] = run_date.strftime('%Y-%m-%dT23')
        else:
            from calendar import monthrange
            
            start_date = logical_date.strftime('%Y-%m-%dT00')
            end_day = monthrange(logical_date.year, logical_date.month)[1]
            end_date = datetime(logical_date.year, logical_date.month, end_day)
            end_date = end_date.strftime('%Y-%m-%dT23')
            

            endpoint['directory'] = f"api/{endpoint['type']}/{logical_date.year}/{logical_date.month:02d}/"
            endpoint['dtobject'] = logical_date
            endpoint['start_date'] = start_date
            endpoint['end_date'] = end_date

    return(endpoints)