{{ config(materialized='table') }}

select
    game_date,
    game_state,
    confidence_tier,
    count(*) as suggestion_count,
    sum(case when bet_result = 'win' then 1 else 0 end) as win_count,
    sum(case when bet_result = 'loss' then 1 else 0 end) as loss_count,
    round(
        safe_divide(
            sum(case when bet_result = 'win' then 1 else 0 end),
            nullif(sum(case when bet_result in ('win', 'loss') then 1 else 0 end), 0)
        ),
        4
    ) as win_pct,
    sum(case when clv_result = 'beat_close' then 1 else 0 end) as beat_close_count,
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
group by 1, 2, 3
