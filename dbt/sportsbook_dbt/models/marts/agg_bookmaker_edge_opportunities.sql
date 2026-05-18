{{ config(materialized='table') }}

select
    bookmaker_title,
    count(distinct concat(cast(event_id as string), '|', market_key, '|', outcome_name)) as opportunity_count,
    round(avg(expected_value), 4) as avg_expected_value,
    round(avg(edge), 4) as avg_edge
from {{ ref('agg_suggested_bets_board') }}
where confidence_tier in ('high', 'medium')
  and game_state in ('pregame', 'live')
  and game_date between current_date("America/New_York")
                    and date_add(current_date("America/New_York"), interval 1 day)
group by 1
order by opportunity_count desc, avg_expected_value desc
