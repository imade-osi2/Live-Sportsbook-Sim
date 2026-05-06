{{ config(
    materialized='table',
    partition_by={"field": "game_date", "data_type": "date"},
    cluster_by=["event_id", "bookmaker_title", "market_key"]
) }}

with ranked as (
    select
        o.event_id,
        date(o.commence_time, "America/New_York") as game_date,
        datetime(o.commence_time, "America/New_York") as commence_time_et,
        concat(o.away_team, ' vs ', o.home_team) as matchup,
        o.home_team,
        o.away_team,
        o.bookmaker_title,
        o.market_key,
        o.outcome_name,
        o.price,
        o.point,
        o.last_update,
        row_number() over (
            partition by o.event_id, o.bookmaker_title, o.market_key, o.outcome_name
            order by o.last_update desc
        ) as rn
    from {{ ref('fact_real_odds_history') }} o
)

select
    event_id,
    game_date,
    commence_time_et,
    matchup,
    home_team,
    away_team,
    bookmaker_title,
    market_key,
    outcome_name,
    price,
    point,
    last_update
from ranked
where rn = 1