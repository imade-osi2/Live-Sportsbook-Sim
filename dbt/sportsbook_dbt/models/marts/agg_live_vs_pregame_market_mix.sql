{{ config(materialized='table') }}

select
    game_state,
    count(distinct event_id) as game_count
from {{ ref('agg_live_market_board') }}
where game_date between current_date("America/New_York")
                  and date_add(current_date("America/New_York"), interval 1 day)
  and game_state in ('pregame', 'live', 'final')
group by 1
order by game_count desc