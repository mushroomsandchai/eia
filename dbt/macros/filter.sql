{% macro get_filter(window_days) %}
    where
        (
            date('{{ var("run_date") }}') = current_date()
            and recorded_date >= current_date() - interval {{ window_days }} day
        )
        or
        (
            date('{{ var("run_date") }}') != current_date()
            and recorded_date > (select max(recorded_date) from {{ this }})
            )
{% endmacro %}