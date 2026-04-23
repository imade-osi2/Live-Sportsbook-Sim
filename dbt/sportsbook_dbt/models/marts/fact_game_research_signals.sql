with market as (
    select
        event_id,
        matchup,
        game_state,
        bookmaker_title,
        outcome_name,
        latest_h2h_price
    from {{ ref('agg_live_market_board') }}
),

grouped_market as (
    select
        event_id,
        matchup,
        game_state,
        min(latest_h2h_price) as best_favorite_price,
        max(latest_h2h_price) as best_underdog_price,
        count(*) as bookmaker_outcome_rows
    from market
    group by 1, 2, 3
),

scores as (
    select
        event_id,
        home_team,
        away_team,
        home_score,
        away_score,
        completed,
        winning_team
    from {{ ref('fact_final_game_results') }}
),

suggestions as (
    select
        event_id,
        count(*) as positive_suggestion_count,
        max(expected_value) as best_expected_value,
        max(edge) as best_edge
    from {{ ref('fact_bet_suggestions') }}
    group by 1
)

select
    e.event_id,
    e.game_date,
    e.commence_time,
    e.matchup,
    m.game_state,
    s.home_team,
    s.away_team,
    s.home_score,
    s.away_score,
    s.completed,
    s.winning_team,
    m.best_favorite_price,
    m.best_underdog_price,
    m.bookmaker_outcome_rows,
    coalesce(g.positive_suggestion_count, 0) as positive_suggestion_count,
    g.best_expected_value,
    g.best_edge,

    case
        when m.best_underdog_price >= 300 then 'high_upside_underdog'
        when m.best_underdog_price between 150 and 299 then 'moderate_underdog'
        when m.best_favorite_price <= -250 then 'heavy_favorite'
        else 'balanced_market'
    end as market_shape_signal,

    case
        when coalesce(g.best_edge, 0) >= 0.03 then 'strong_edge'
        when coalesce(g.best_edge, 0) >= 0.015 then 'moderate_edge'
        else 'weak_edge'
    end as pricing_signal,

    case
        when m.game_state = 'live' and s.home_score is not null and s.away_score is not null
            then 'live_game_with_score_context'
        when m.game_state = 'pregame'
            then 'pregame_market_only'
        when m.game_state = 'final'
            then 'completed_game_review'
        else 'limited_context'
    end as context_signal,

    case
        when coalesce(g.best_edge, 0) >= 0.03 and m.best_underdog_price >= 200
            then 'Potential plus-money value with strong model edge'
        when coalesce(g.best_edge, 0) >= 0.03 and m.best_favorite_price <= -250
            then 'Model favors a strong market favorite despite expensive price'
        when coalesce(g.best_edge, 0) >= 0.015
            then 'Some positive value present, but not a top-tier signal'
        else 'No strong value signal yet'
    end as research_summary

from {{ ref('dim_events') }} e
left join grouped_market m
    on e.event_id = m.event_id
left join scores s
    on e.event_id = s.event_id
left join suggestions g
    on e.event_id = g.event_id