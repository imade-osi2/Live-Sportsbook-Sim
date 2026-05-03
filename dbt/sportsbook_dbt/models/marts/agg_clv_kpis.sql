{{ config(materialized='table') }}

select
    count(*) as total_suggestions,
    sum(case when clv_result = 'beat_close' then 1 else 0 end) as beat_close_count,
    sum(case when clv_result = 'push_close' then 1 else 0 end) as push_close_count,
    sum(case when clv_result = 'lost_close' then 1 else 0 end) as lost_close_count,
    round(
        safe_divide(
            sum(case when clv_result = 'beat_close' then 1 else 0 end),
            count(*)
        ),
        4
    ) as beat_close_pct,
    round(avg(edge), 4) as avg_edge,
    round(avg(expected_value), 4) as avg_expected_value
from {{ ref('fact_bet_evaluation') }}