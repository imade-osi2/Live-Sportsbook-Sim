select
    score_record_id,
    event_id,
    sport_key,
    sport_title,
    commence_time,
    completed,
    home_team,
    away_team,
    home_score,
    away_score,
    last_update
from {{ ref('stg_nba_scores_api') }}