select
    event_id,
    sport_key,
    sport_title,
    cast(commence_time as timestamp) as commence_time,
    home_team,
    away_team,
    created_at
from {{ source('raw_market', 'raw_nba_events_api') }}