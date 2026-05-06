{{ config(
    materialized='table',
    partition_by={"field": "game_date", "data_type": "date"},
    cluster_by=["event_id", "market_key", "outcome_name"]
) }}

with latest_prices as (
    select
        event_id,
        game_date,
        commence_time_et,
        matchup,
        case
            when game_date = current_date("America/New_York") then 'today'
            when game_date = date_add(current_date("America/New_York"), interval 1 day) then 'tomorrow'
            else 'other'
        end as slate_bucket,
        market_key,
        outcome_name,
        bookmaker_title,
        price,
        point,
        case
            when price < 0 then abs(price) / (abs(price) + 100.0)
            else 100.0 / (price + 100.0)
        end as implied_prob
    from {{ ref('agg_latest_real_odds_by_game') }}
    where game_date between current_date("America/New_York")
                      and date_add(current_date("America/New_York"), interval 1 day)
),

ranked as (
    select
        *,
        row_number() over (
            partition by event_id, market_key, outcome_name
            order by price desc
        ) as best_rank,
        row_number() over (
            partition by event_id, market_key, outcome_name
            order by price asc
        ) as worst_rank
    from latest_prices
),

best_prices as (
    select
        event_id,
        game_date,
        commence_time_et,
        matchup,
        slate_bucket,
        market_key,
        outcome_name,
        bookmaker_title as best_bookmaker,
        price as best_price,
        point as best_point,
        implied_prob as best_implied_prob
    from ranked
    where best_rank = 1
),

worst_prices as (
    select
        event_id,
        market_key,
        outcome_name,
        bookmaker_title as worst_bookmaker,
        price as worst_price,
        implied_prob as worst_implied_prob
    from ranked
    where worst_rank = 1
)

select
    b.event_id,
    b.game_date,
    b.commence_time_et,
    b.matchup,
    b.slate_bucket,
    b.market_key,
    b.outcome_name,
    b.best_bookmaker,
    b.best_price,
    b.best_point,
    w.worst_bookmaker,
    w.worst_price,
    b.best_price - w.worst_price as price_gap,
    round(abs(b.best_implied_prob - w.worst_implied_prob) * 100, 2) as implied_prob_gap_pp
from best_prices b
left join worst_prices w
    on b.event_id = w.event_id
   and b.market_key = w.market_key
   and b.outcome_name = w.outcome_name