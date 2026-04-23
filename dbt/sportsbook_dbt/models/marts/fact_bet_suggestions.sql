with market_prices as (
    select
        event_id,
        game_date,
        commence_time,
        matchup,
        game_state,
        bookmaker_title,
        market_key,
        outcome_name,
        price,
        point,
        last_update
    from {{ ref('agg_latest_real_odds_by_game') }} o
    left join (
        select distinct
            event_id,
            matchup,
            game_state
        from {{ ref('agg_live_market_board') }}
    ) b
        using (event_id, matchup)
),

priced as (
    select
        event_id,
        game_date,
        commence_time,
        matchup,
        game_state,
        bookmaker_title,
        market_key,
        outcome_name,
        price,
        point,
        last_update,

        case
            when price < 0 then abs(price) / (abs(price) + 100.0)
            else 100.0 / (price + 100.0)
        end as implied_probability
    from market_prices
),

modeled as (
    select
        *,
        case
            when market_key = 'h2h' and price >= 200 then implied_probability + 0.035
            when market_key = 'h2h' and price between 120 and 199 then implied_probability + 0.025
            when market_key = 'spreads' then implied_probability + 0.015
            when market_key = 'totals' then implied_probability + 0.010
            else implied_probability + 0.005
        end as estimated_fair_probability
    from priced
),

scored as (
    select
        *,
        estimated_fair_probability - implied_probability as edge,
        (estimated_fair_probability * 
            case
                when price > 0 then price / 100.0
                else 100.0 / abs(price)
            end
        ) - (1 - estimated_fair_probability) as expected_value
    from modeled
)

select
    event_id,
    game_date,
    commence_time,
    matchup,
    game_state,
    bookmaker_title,
    market_key,
    outcome_name,
    price,
    point,
    last_update,
    implied_probability,
    estimated_fair_probability,
    edge,
    expected_value,
    case
        when edge >= 0.03 and expected_value > 0.05 then 'high'
        when edge >= 0.015 and expected_value > 0.01 then 'medium'
        else 'low'
    end as confidence_tier,
    case
        when market_key = 'h2h' and edge >= 0.03 then 'Underdog or plus-money value versus implied market probability'
        when market_key = 'spreads' and edge >= 0.015 then 'Spread price shows moderate edge over implied probability'
        when market_key = 'totals' and edge >= 0.01 then 'Totals market shows smaller but positive estimated edge'
        else 'Monitor only, weak edge'
    end as rationale
from scored
where expected_value > 0