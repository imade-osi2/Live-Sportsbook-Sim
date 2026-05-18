{{ config(materialized='table') }}

select
    confidence_tier,
    market_key,
    count(distinct concat(cast(event_id as string), '|', outcome_name)) as signal_count
from {{ ref('agg_suggested_bets_board') }}
where game_state in ('pregame', 'live')
  and game_date between current_date("America/New_York")
                    and date_add(current_date("America/New_York"), interval 1 day)
group by 1, 2
order by
    case confidence_tier
        when 'high' then 1
        when 'medium' then 2
        when 'low' then 3
        else 4
    end,
    market_key
