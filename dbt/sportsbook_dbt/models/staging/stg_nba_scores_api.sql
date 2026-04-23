select
    score_record_id,
    event_id,
    sport_key,
    sport_title,
    cast(commence_time as timestamp) as commence_time,
    completed,
    home_team,
    away_team,
    cast(home_score as int64) as home_score,
    cast(away_score as int64) as away_score,
    cast(last_update as timestamp) as last_update,
    created_at
from {{ source('raw_market', 'raw_nba_scores_api') }}