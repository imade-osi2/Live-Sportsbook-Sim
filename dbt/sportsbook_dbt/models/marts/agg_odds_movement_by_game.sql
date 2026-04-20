select
    game_id,
    home_team,
    away_team,
    min(home_odds) as min_home_odds,
    max(home_odds) as max_home_odds,
    min(away_odds) as min_away_odds,
    max(away_odds) as max_away_odds,
    count(*) as odds_update_count
from {{ ref('fact_odds_history') }}
group by 1, 2, 3