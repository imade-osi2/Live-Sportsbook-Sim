select
    game_id,
    game_date,
    season,
    home_team,
    away_team,
    concat(home_team, ' vs ', away_team) as matchup,
    game_status,
    home_score,
    away_score
from {{ ref('stg_nba_games') }}