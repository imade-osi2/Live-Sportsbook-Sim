{{ config(
    materialized='table',
    partition_by={"field": "game_date", "data_type": "date"},
    cluster_by=["event_id", "home_team", "away_team"]
) }}

select
    event_id,
    sport_key,
    sport_title,
    commence_time,
    datetime(commence_time, "America/New_York") as commence_time_et,
    date(commence_time, "America/New_York") as game_date,
    home_team,
    away_team,
    concat(away_team, ' vs ', home_team) as matchup
from {{ ref('stg_nba_events_api') }}