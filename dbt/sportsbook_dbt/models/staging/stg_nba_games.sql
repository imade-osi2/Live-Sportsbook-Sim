select
    game_id,
    game_date,
    season,
    home_team,
    away_team,
    game_status,
    home_score,
    away_score,
    created_at
from {{ source('raw', 'raw_nba_games') }}