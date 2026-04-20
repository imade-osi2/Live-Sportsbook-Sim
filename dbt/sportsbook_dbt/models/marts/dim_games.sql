select
    game_id,
    game_date,
    season,
    home_team,
    away_team,
    game_status,
    home_score,
    away_score
from {{ ref('stg_nba_games') }}