{{ config(materialized='table') }}

select
    game_date,
    round(avg(clv_win_flag) * 100, 2) as clv_pct
from {{ ref('fact_bet_evaluation') }}
group by 1
order by 1