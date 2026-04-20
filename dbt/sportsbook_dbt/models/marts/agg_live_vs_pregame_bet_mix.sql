select
    case
        when g.game_status = 'in_progress' then 'live'
        else 'pregame'
    end as bet_timing,
    count(*) as total_bets,
    sum(b.stake) as total_handle,
    avg(b.stake) as avg_stake
from {{ ref('fact_bets') }} b
left join {{ ref('dim_games') }} g
    on b.game_id = g.game_id
group by 1