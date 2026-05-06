{{ config(
    materialized='table',
    partition_by={"field": "game_date", "data_type": "date"},
    cluster_by=["event_id", "bookmaker_title", "market_key", "bet_result"]
) }}

with entry_prices as (
    select *
    from (
        select
            event_id,
            bookmaker_title,
            market_key,
            outcome_name,
            price as entry_price,
            point as entry_point,
            last_update as entry_last_update,
            row_number() over (
                partition by event_id, bookmaker_title, market_key, outcome_name
                order by last_update asc
            ) as rn
        from {{ ref('fact_real_odds_history') }}
    )
    where rn = 1
),

closing_prices as (
    select *
    from (
        select
            event_id,
            bookmaker_title,
            market_key,
            outcome_name,
            price as closing_price_proxy,
            point as closing_point_proxy,
            last_update as closing_last_update,
            row_number() over (
                partition by event_id, bookmaker_title, market_key, outcome_name
                order by last_update desc
            ) as rn
        from {{ ref('fact_real_odds_history') }}
    )
    where rn = 1
),

latest_results as (
    select
        event_id,
        home_score,
        away_score,
        completed,
        case
            when home_score > away_score then home_team
            when away_score > home_score then away_team
            else 'push'
        end as winning_team
    from {{ ref('fact_final_game_results') }}
)

select
    s.event_id,
    s.game_date,
    s.commence_time_et,
    s.matchup,
    s.game_state,
    s.bookmaker_title,
    s.market_key,
    s.outcome_name,
    coalesce(e.entry_price, s.price) as suggested_price,
    coalesce(e.entry_point, s.point) as suggested_point,
    s.implied_probability,
    s.estimated_fair_probability,
    s.edge,
    s.expected_value,
    s.confidence_tier,
    s.rationale,
    c.closing_price_proxy,
    c.closing_point_proxy,

    case
        when coalesce(e.entry_price, s.price) > c.closing_price_proxy then 'beat_close'
        when coalesce(e.entry_price, s.price) = c.closing_price_proxy then 'push_close'
        else 'lost_close'
    end as clv_result,

    case
        when coalesce(e.entry_price, s.price) > c.closing_price_proxy then 1
        else 0
    end as clv_win_flag,

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
left join entry_prices e
    on s.event_id = e.event_id
   and s.bookmaker_title = e.bookmaker_title
   and s.market_key = e.market_key
   and s.outcome_name = e.outcome_name
left join closing_prices c
    on s.event_id = c.event_id
   and s.bookmaker_title = c.bookmaker_title
   and s.market_key = c.market_key
   and s.outcome_name = c.outcome_name
left join latest_results r
    on s.event_id = r.event_id