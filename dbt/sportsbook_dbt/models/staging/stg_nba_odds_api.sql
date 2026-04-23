select
    odds_record_id,
    event_id,
    sport_key,
    cast(commence_time as timestamp) as commence_time,
    home_team,
    away_team,
    bookmaker_key,
    bookmaker_title,
    market_key,
    outcome_name,
    cast(price as float64) as price,
    cast(point as float64) as point,
    cast(last_update as timestamp) as last_update,
    created_at
from {{ source('raw_market', 'raw_nba_odds_api') }}