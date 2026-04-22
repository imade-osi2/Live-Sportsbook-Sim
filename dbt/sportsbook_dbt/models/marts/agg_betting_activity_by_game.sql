select
    b.game_id,
    g.game_date,
    g.home_team,
    g.away_team,
    concat(g.home_team, ' vs ', g.away_team) as matchup,
    g.game_status,
    count(*) as total_bets,
    sum(b.stake) as total_handle,
    avg(b.stake) as avg_stake
from {{ ref('fact_bets') }} b
left join {{ ref('dim_games') }} g
    on b.game_id = g.game_id
group by 1, 2, 3, 4, 5, 6