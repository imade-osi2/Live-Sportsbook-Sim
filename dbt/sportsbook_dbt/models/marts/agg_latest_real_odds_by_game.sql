{{ config(
    materialized='table',
    partition_by={"field": "game_date", "data_type": "date"},
    cluster_by=["event_id", "bookmaker_title", "market_key"]
) }}

with ranked as (
    select
        event_id,
        commence_time,
        home_team,
        away_team,
        concat(home_team, ' vs ', away_team) as matchup,
        bookmaker_title,
        market_key,
        outcome_name,
        price,
        point,
        last_update,
        row_number() over (
            partition by event_id, bookmaker_title, market_key, outcome_name
            order by last_update desc
        ) as rn
    from {{ ref('fact_real_odds_history') }}
)

select
    event_id,
    date(commence_time) as game_date,
    commence_time,
    home_team,
    away_team,
    matchup,
    bookmaker_title,
    market_key,
    outcome_name,
    price,
    point,
    last_update
from ranked
where rn = 1