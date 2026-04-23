with ranked as (
    select
        event_id,
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
    bookmaker_title,
    market_key,
    outcome_name,
    price as closing_price_proxy,
    point as closing_point_proxy,
    last_update as closing_last_update
from ranked
where rn = 1