select
    game_id,
    home_team,
    away_team,
    count(*) as total_bets,
    sum(stake) as total_handle,
    avg(stake) as avg_stake
from {{ ref('fact_bets') }}
group by 1, 2, 3