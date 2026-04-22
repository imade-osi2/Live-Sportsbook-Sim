with ranked_odds as (
    select
        o.game_id,
        g.game_date,
        g.home_team,
        g.away_team,
        concat(g.home_team, ' vs ', g.away_team) as matchup,
        g.game_status,
        o.sportsbook,
        o.market_type,
        o.home_odds,
        o.away_odds,
        o.spread,
        o.total_points,
        o.event_time,
        row_number() over (
            partition by o.game_id
            order by o.event_time desc
        ) as rn
    from {{ ref('fact_odds_history') }} o
    left join {{ ref('dim_games') }} g
        on o.game_id = g.game_id
)

select
    game_id,
    game_date,
    home_team,
    away_team,
    matchup,
    game_status,
    sportsbook,
    market_type,
    home_odds as latest_home_odds,
    away_odds as latest_away_odds,
    spread as latest_spread,
    total_points as latest_total_points,
    event_time as last_odds_update_time
from ranked_odds
where rn = 1