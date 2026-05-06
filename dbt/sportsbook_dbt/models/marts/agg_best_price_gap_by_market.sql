{{ config(materialized='table') }}

select
    market_key,
    round(avg(implied_prob_gap_pp), 2) as avg_gap_pp
from {{ ref('agg_best_price_by_outcome') }}
group by 1
order by avg_gap_pp desc