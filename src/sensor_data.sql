CREATE TABLE sensor_data (
    event_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    temperature DECIMAL(5, 2) NOT NULL
);
CREATE TABLE action_data (
    event_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    temperature VARCHAR(25) NOT NULL
);
