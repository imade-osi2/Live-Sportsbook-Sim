{{ config(materialized='table') }}

select
    game_id,
    game_date,
    concat(away_team, ' vs ', home_team) as matchup,
    count(*) as bet_count,
    count(distinct user_id) as bettor_count,
    round(sum(stake), 2) as total_stake,
    round(avg(stake), 2) as avg_stake,
    round(
        sum(
            case
                when odds > 0 then stake * (odds / 100.0)
                when odds < 0 then stake * (100.0 / abs(odds))
                else 0
            end
        ),
        2
    ) as total_potential_profit
from {{ ref('fact_bets') }}
group by 1, 2, 3
