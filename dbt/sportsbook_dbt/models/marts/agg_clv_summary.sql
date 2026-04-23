select
    bookmaker_title,
    market_key,
    confidence_tier,
    count(*) as total_suggestions,
    sum(case when clv_result = 'beat_close' then 1 else 0 end) as beat_close_count,
    sum(case when clv_result = 'push_close' then 1 else 0 end) as push_close_count,
    sum(case when clv_result = 'lost_close' then 1 else 0 end) as lost_close_count
from {{ ref('fact_bet_evaluation') }}
group by 1, 2, 3