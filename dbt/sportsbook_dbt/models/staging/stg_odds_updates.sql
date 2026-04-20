select
    odds_event_id,
    game_id,
    sportsbook,
    market_type,
    home_odds,
    away_odds,
    spread,
    total_points,
    event_time,
    ingested_at
from {{ source('raw', 'raw_odds_updates_stream') }}