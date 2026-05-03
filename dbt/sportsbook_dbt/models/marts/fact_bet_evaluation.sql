{{ config(
    materialized='table',
    partition_by={"field": "game_date", "data_type": "date"},
    cluster_by=["event_id", "bookmaker_title", "market_key",  "bet_result"]
) }}

select
    s.event_id,
    s.game_date,
    s.commence_time,
    s.matchup,
    s.game_state,
    s.bookmaker_title,
    s.market_key,
    s.outcome_name,
    s.price as suggested_price,
    s.point as suggested_point,
    s.implied_probability,
    s.estimated_fair_probability,
    s.edge,
    s.expected_value,
    s.confidence_tier,
    s.rationale,
    c.closing_price_proxy,
    c.closing_point_proxy,

    case
        when s.price > c.closing_price_proxy then 'beat_close'
        when s.price = c.closing_price_proxy then 'push_close'
        else 'lost_close'
    end as clv_result,

    r.home_score,
    r.away_score,
    r.completed,
    r.winning_team,

    case
        when s.market_key = 'h2h' and s.outcome_name = r.winning_team then 'win'
        when s.market_key = 'h2h' and r.completed = true then 'loss'
        else null
    end as bet_result

from {{ ref('fact_bet_suggestions') }} s
left join {{ ref('fact_closing_odds_proxy') }} c
    on s.event_id = c.event_id
   and s.bookmaker_title = c.bookmaker_title
   and s.market_key = c.market_key
   and s.outcome_name = c.outcome_name
left join {{ ref('fact_final_game_results') }} r
    on s.event_id = r.event_id