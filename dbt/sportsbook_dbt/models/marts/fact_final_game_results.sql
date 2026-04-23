with latest_scores as (
    select *
    from (
        select
            event_id,
            home_team,
            away_team,
            home_score,
            away_score,
            completed,
            last_update,
            row_number() over (
                partition by event_id
                order by last_update desc nulls last
            ) as rn
        from {{ ref('fact_real_scores') }}
    )
    where rn = 1
)

select
    event_id,
    home_team,
    away_team,
    home_score,
    away_score,
    completed,
    case
        when home_score > away_score then home_team
        when away_score > home_score then away_team
        else 'push'
    end as winning_team
from latest_scores