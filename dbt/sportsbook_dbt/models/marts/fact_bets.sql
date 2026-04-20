select
    b.bet_id,
    b.user_id,
    b.game_id,
    g.game_date,
    g.home_team,
    g.away_team,
    b.market_type,
    b.selection,
    b.stake,
    b.odds,
    b.bet_time,
    b.ingested_at
from {{ ref('stg_bet_events') }} b
left join {{ ref('stg_nba_games') }} g
    on b.game_id = g.game_id