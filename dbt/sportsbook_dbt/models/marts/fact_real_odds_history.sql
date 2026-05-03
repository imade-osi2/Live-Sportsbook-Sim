{{ config(
    materialized='table',
    partition_by={"field": "last_update", "data_type": "timestamp", "granularity": "day"},
    cluster_by=["event_id", "bookmaker_title", "market_key"]
) }}

select
    odds_record_id,
    event_id,
    sport_key,
    commence_time,
    home_team,
    away_team,
    bookmaker_key,
    bookmaker_title,
    market_key,
    outcome_name,
    price,
    point,
    last_update
from {{ ref('stg_nba_odds_api') }}