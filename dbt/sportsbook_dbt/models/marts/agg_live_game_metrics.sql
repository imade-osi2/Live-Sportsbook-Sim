{{ config(
    materialized='table',
    partition_by={"field": "game_date", "data_type": "date"},
    cluster_by=["event_id", "game_state", "bookmaker_title"]
) }}

select
    event_id,
    game_date,
    commence_time,
    matchup,
    game_state,
    bookmaker_title,
    outcome_name,
    latest_h2h_price,
    home_score,
    away_score,
    odds_last_update
from {{ ref('agg_live_market_board') }}
where game_state in ('live', 'final')