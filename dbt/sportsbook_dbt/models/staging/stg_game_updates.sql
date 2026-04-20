select
    game_event_id,
    game_id,
    game_status,
    home_score,
    away_score,
    event_time,
    ingested_at
from {{ source('raw', 'raw_game_updates_stream') }}