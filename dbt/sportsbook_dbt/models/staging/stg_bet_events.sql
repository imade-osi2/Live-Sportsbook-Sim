select
    bet_id,
    user_id,
    game_id,
    market_type,
    selection,
    stake,
    odds,
    bet_time,
    ingested_at
from {{ source('raw', 'raw_bet_events_stream') }}