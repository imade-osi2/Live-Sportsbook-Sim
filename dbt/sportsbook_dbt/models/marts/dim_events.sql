select
    event_id,
    sport_key,
    sport_title,
    commence_time,
    date(commence_time) as game_date,
    home_team,
    away_team,
    concat(home_team, ' vs ', away_team) as matchup
from {{ ref('stg_nba_events_api') }}