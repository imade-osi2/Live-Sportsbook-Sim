select
    o.odds_event_id,
    o.game_id,
    g.game_date,
    g.home_team,
    g.away_team,
    o.sportsbook,
    o.market_type,
    o.home_odds,
    o.away_odds,
    o.spread,
    o.total_points,
    o.event_time,
    o.ingested_at
from {{ ref('stg_odds_updates') }} o
left join {{ ref('stg_nba_games') }} g
    on o.game_id = g.game_id