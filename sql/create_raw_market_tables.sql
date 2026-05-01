CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.nba_events_api (
    event_id TEXT PRIMARY KEY,
    sport_key TEXT,
    sport_title TEXT,
    commence_time TIMESTAMP,
    home_team TEXT,
    away_team TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.nba_odds_api (
    odds_record_id TEXT PRIMARY KEY,
    event_id TEXT,
    sport_key TEXT,
    commence_time TIMESTAMP,
    home_team TEXT,
    away_team TEXT,
    bookmaker_key TEXT,
    bookmaker_title TEXT,
    market_key TEXT,
    outcome_name TEXT,
    price NUMERIC,
    point NUMERIC,
    last_update TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.nba_scores_api (
    score_record_id TEXT PRIMARY KEY,
    event_id TEXT,
    sport_key TEXT,
    sport_title TEXT,
    commence_time TIMESTAMP,
    completed BOOLEAN,
    home_team TEXT,
    away_team TEXT,
    home_score INT,
    away_score INT,
    last_update TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.bet_events_stream (
    bet_id TEXT PRIMARY KEY,
    user_id TEXT,
    game_id TEXT,
    market_type TEXT,
    selection TEXT,
    stake NUMERIC,
    odds NUMERIC,
    bet_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.odds_updates_stream (
    odds_event_id TEXT PRIMARY KEY,
    game_id TEXT,
    sportsbook TEXT,
    market_type TEXT,
    home_odds NUMERIC,
    away_odds NUMERIC,
    spread NUMERIC,
    total_points NUMERIC,
    event_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.game_updates_stream (
    game_event_id TEXT PRIMARY KEY,
    game_id TEXT,
    game_status TEXT,
    home_score INT,
    away_score INT,
    event_time TIMESTAMP
);