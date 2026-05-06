{{ config(materialized='table') }}

with latest_scores as (
    select *
    from (
        select
            event_id,
            completed,
            home_score,
            away_score,
            last_update,
            row_number() over (
                partition by event_id
                order by last_update desc nulls last
            ) as rn
        from {{ ref('fact_real_scores') }}
    )
    where rn = 1
),

latest_h2h as (
    select *
    from (
        select
            event_id,
            bookmaker_title,
            outcome_name,
            price,
            last_update,
            row_number() over (
                partition by event_id, bookmaker_title, outcome_name
                order by last_update desc
            ) as rn
        from {{ ref('fact_real_odds_history') }}
        where market_key = 'h2h'
    )
    where rn = 1
)

select
    e.event_id,
    e.game_date,
    e.commence_time_et,
    e.home_team,
    e.away_team,
    e.matchup,
    case
        when s.completed = true then 'final'
        when (s.home_score is not null or s.away_score is not null)
             and timestamp_diff(current_timestamp(), h.last_update, hour) <= 6 then 'live'
        when e.game_date between current_date("America/New_York")
                            and date_add(current_date("America/New_York"), interval 1 day)
             then 'pregame'
        else 'historical'
    end as game_state,
    s.home_score,
    s.away_score,
    h.bookmaker_title,
    h.outcome_name,
    h.price as latest_h2h_price,
    h.last_update as odds_last_update
from {{ ref('dim_events') }} e
left join latest_scores s
    on e.event_id = s.event_id
left join latest_h2h h
    on e.event_id = h.event_id
where h.event_id is not null