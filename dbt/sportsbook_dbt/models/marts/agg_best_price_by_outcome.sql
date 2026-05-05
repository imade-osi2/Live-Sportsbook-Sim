{{ config(
    materialized='table',
    partition_by={"field": "game_date", "data_type": "date"},
    cluster_by=["event_id", "market_key", "outcome_name"]
) }}


with ranked_prices as (
    select
        a.event_id,
        a.game_date,
        a.commence_time,
        a.matchup,
        lmb.game_state,
        a.market_key,
        a.outcome_name,
        a.bookmaker_title,
        a.price,
        a.point,
        a.last_update,
        row_number() over (
            partition by a.event_id, a.market_key, a.outcome_name
            order by a.price desc
        ) as best_price_rank,
        row_number() over (
            partition by a.event_id, a.market_key, a.outcome_name
            order by a.price asc
        ) as worst_price_rank
    from {{ ref('agg_latest_real_odds_by_game') }} a
    left join {{ ref('agg_live_market_board') }} lmb
        on a.event_id = lmb.event_id
),

best_prices as (
    select
        event_id,
        game_date,
        commence_time,
        matchup,
        game_state,
        market_key,
        outcome_name,
        bookmaker_title as best_bookmaker,
        price as best_price,
        point as best_point,
        last_update as best_price_last_update
    from ranked_prices
    where best_price_rank = 1
),

worst_prices as (
    select
        event_id,
        market_key,
        outcome_name,
        bookmaker_title as worst_bookmaker,
        price as worst_price
    from ranked_prices
    where worst_price_rank = 1
)

select
    b.event_id,
    b.game_date,
    b.commence_time,
    b.matchup,
    b.game_state,
    b.market_key,
    b.outcome_name,
    b.best_bookmaker,
    b.best_price,
    b.best_point,
    w.worst_bookmaker,
    w.worst_price,
    b.best_price - w.worst_price as price_gap,
    b.best_price_last_update
from best_prices b
left join worst_prices w
    on b.event_id = w.event_id
   and b.market_key = w.market_key
   and b.outcome_name = w.outcome_name