select
    event_id,
    game_date,
    commence_time,
    matchup,
    game_state,
    home_score,
    away_score,
    market_shape_signal,
    pricing_signal,
    context_signal,
    positive_suggestion_count,
    round(best_expected_value, 4) as best_expected_value,
    round(best_edge, 4) as best_edge,
    research_summary
from {{ ref('fact_game_research_signals') }}
order by
    best_expected_value desc nulls last,
    best_edge desc nulls last,
    game_date asc