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
    round(implied_probability, 4) as implied_probability,
    round(estimated_fair_probability, 4) as estimated_fair_probability,
    round(edge, 4) as edge,
    round(expected_value, 4) as expected_value,
    confidence_tier,
    rationale,
    last_update
from {{ ref('fact_bet_suggestions') }}
where confidence_tier in ('high', 'medium')
order by expected_value desc, edge desc