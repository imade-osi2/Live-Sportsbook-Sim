with suggestion_stats as (
    select
        count(*) as total_suggestions,
        avg(expected_value) as avg_expected_value,
        avg(edge) as avg_edge,
        sum(case when confidence_tier = 'high' then 1 else 0 end) as high_confidence_suggestions
    from {{ ref('fact_bet_suggestions') }}
),

evaluation_stats as (
    select
        sum(case when bet_result = 'win' then 1 else 0 end) as total_wins,
        sum(case when bet_result = 'loss' then 1 else 0 end) as total_losses,
        sum(case when clv_result = 'beat_close' then 1 else 0 end) as beat_close_count
    from {{ ref('fact_bet_evaluation') }}
),

market_stats as (
    select
        count(distinct event_id) as active_games,
        count(distinct bookmaker_title) as bookmakers_tracked
    from {{ ref('agg_latest_real_odds_by_game') }}
)

select
    m.active_games,
    m.bookmakers_tracked,
    s.total_suggestions,
    s.high_confidence_suggestions,
    round(s.avg_expected_value, 4) as avg_expected_value,
    round(s.avg_edge, 4) as avg_edge,
    e.total_wins,
    e.total_losses,
    e.beat_close_count
from market_stats m
cross join suggestion_stats s
cross join evaluation_stats e