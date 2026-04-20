select
    market_type,
    count(*) as total_bets,
    sum(stake) as total_handle,
    avg(stake) as avg_stake
from {{ ref('fact_bets') }}
group by 1