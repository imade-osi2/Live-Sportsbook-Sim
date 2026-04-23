select
    bookmaker_title,
    market_key,
    confidence_tier,
    count(*) as total_suggestions,
    avg(edge) as avg_edge,
    avg(expected_value) as avg_expected_value,
    sum(case when bet_result = 'win' then 1 else 0 end) as wins,
    sum(case when bet_result = 'loss' then 1 else 0 end) as losses
from {{ ref('fact_bet_evaluation') }}
group by 1, 2, 3