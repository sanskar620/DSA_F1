-- F1 StrategyIQ Database Schema

DROP TABLE IF EXISTS race_control CASCADE;
DROP TABLE IF EXISTS weather CASCADE;
DROP TABLE IF EXISTS pit_stops CASCADE;
DROP TABLE IF EXISTS tyre_stints CASCADE;
DROP TABLE IF EXISTS laps CASCADE;
DROP TABLE IF EXISTS results CASCADE;
DROP TABLE IF EXISTS races CASCADE;
DROP TABLE IF EXISTS constructors CASCADE;
DROP TABLE IF EXISTS drivers CASCADE;
DROP TABLE IF EXISTS circuits CASCADE;

-- 1. circuits
CREATE TABLE IF NOT EXISTS circuits (
    circuit_id INT PRIMARY KEY,
    circuit_name VARCHAR(255) NOT NULL,
    locality VARCHAR(255),
    country VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT
);

-- 2. drivers
CREATE TABLE IF NOT EXISTS drivers (
    driver_id INT PRIMARY KEY,
    driver_code VARCHAR(10),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    nationality VARCHAR(255),
    permanent_number INT
);

-- 3. constructors
CREATE TABLE IF NOT EXISTS constructors (
    constructor_id INT PRIMARY KEY,
    constructor_name VARCHAR(255) NOT NULL,
    nationality VARCHAR(255)
);

-- 4. races
CREATE TABLE IF NOT EXISTS races (
    race_id INT PRIMARY KEY,
    season INT NOT NULL CHECK (season >= 1950 AND season <= 2100),
    round INT NOT NULL CHECK (round > 0),
    circuit_id INT NOT NULL REFERENCES circuits(circuit_id),
    race_name VARCHAR(255) NOT NULL,
    race_date DATE NOT NULL,
    race_time TIME,
    UNIQUE(season, round)
);

-- 5. results
CREATE TABLE IF NOT EXISTS results (
    result_id INT PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    driver_id INT NOT NULL REFERENCES drivers(driver_id),
    constructor_id INT NOT NULL REFERENCES constructors(constructor_id),
    grid_position INT,
    finish_position INT CHECK (finish_position > 0 OR finish_position IS NULL),
    points FLOAT CHECK (points >= 0),
    laps_completed INT CHECK (laps_completed >= 0),
    status VARCHAR(255),
    race_time_ms BIGINT,
    fastest_lap INT,
    fastest_lap_rank INT
);

-- 6. laps
CREATE TABLE IF NOT EXISTS laps (
    lap_id SERIAL PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    driver_id INT NOT NULL REFERENCES drivers(driver_id),
    lap_number INT NOT NULL CHECK (lap_number > 0),
    lap_time_ms BIGINT,
    sector1_ms BIGINT,
    sector2_ms BIGINT,
    sector3_ms BIGINT,
    position INT,
    UNIQUE(race_id, driver_id, lap_number)
);

-- 7. tyre_stints
CREATE TABLE IF NOT EXISTS tyre_stints (
    stint_id SERIAL PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    driver_id INT NOT NULL REFERENCES drivers(driver_id),
    stint_number INT NOT NULL CHECK (stint_number > 0),
    compound VARCHAR(50),
    start_lap INT,
    end_lap INT,
    tyre_age_start INT,
    tyre_age_end INT,
    UNIQUE(race_id, driver_id, stint_number)
);

-- 8. pit_stops
CREATE TABLE IF NOT EXISTS pit_stops (
    pit_stop_id SERIAL PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    driver_id INT NOT NULL REFERENCES drivers(driver_id),
    lap INT NOT NULL CHECK (lap > 0),
    stop_number INT NOT NULL CHECK (stop_number > 0),
    pit_duration_ms BIGINT,
    UNIQUE(race_id, driver_id, stop_number)
);

-- 9. weather
CREATE TABLE IF NOT EXISTS weather (
    weather_id SERIAL PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    timestamp TIMESTAMP NOT NULL,
    air_temperature FLOAT,
    track_temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    wind_speed FLOAT,
    wind_direction FLOAT,
    rainfall FLOAT,
    UNIQUE(race_id, timestamp)
);

-- 10. race_control
CREATE TABLE IF NOT EXISTS race_control (
    event_id SERIAL PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    lap INT,
    timestamp TIMESTAMP NOT NULL,
    event_type VARCHAR(255),
    message TEXT,
    UNIQUE(race_id, timestamp, message)
);

-- Indexes for frequently queried fields
CREATE INDEX IF NOT EXISTS idx_races_season ON races(season);
CREATE INDEX IF NOT EXISTS idx_races_circuit_id ON races(circuit_id);

CREATE INDEX IF NOT EXISTS idx_results_race_id ON results(race_id);
CREATE INDEX IF NOT EXISTS idx_results_driver_id ON results(driver_id);
CREATE INDEX IF NOT EXISTS idx_results_constructor_id ON results(constructor_id);

CREATE INDEX IF NOT EXISTS idx_laps_race_driver ON laps(race_id, driver_id);
CREATE INDEX IF NOT EXISTS idx_laps_race_lap ON laps(race_id, lap_number);

CREATE INDEX IF NOT EXISTS idx_tyre_stints_race_driver ON tyre_stints(race_id, driver_id);

CREATE INDEX IF NOT EXISTS idx_pit_stops_race_driver ON pit_stops(race_id, driver_id);

CREATE INDEX IF NOT EXISTS idx_weather_race_timestamp ON weather(race_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_race_control_race_lap ON race_control(race_id, lap);
