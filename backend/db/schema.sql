CREATE TABLE IF NOT EXISTS districts (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL,
    area_km2 DOUBLE PRECISION,
    boundary_geojson JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS environmental_metrics (
    id BIGSERIAL PRIMARY KEY,
    district_id BIGINT NOT NULL REFERENCES districts(id),
    observed_month DATE NOT NULL,
    average_ndvi DOUBLE PRECISION,
    rainfall_mm DOUBLE PRECISION,
    water_percent DOUBLE PRECISION,
    water_area_km2 DOUBLE PRECISION,
    source TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (district_id, observed_month)
);

CREATE TABLE IF NOT EXISTS prediction_runs (
    id BIGSERIAL PRIMARY KEY,
    district_id BIGINT NOT NULL REFERENCES districts(id),
    target_month DATE NOT NULL,
    predicted_ndvi DOUBLE PRECISION,
    predicted_rainfall_mm DOUBLE PRECISION,
    predicted_water_percent DOUBLE PRECISION,
    model_name TEXT NOT NULL,
    training_source TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_training_runs (
    id BIGSERIAL PRIMARY KEY,
    district_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    training_source TEXT NOT NULL,
    train_records INTEGER NOT NULL,
    test_records INTEGER NOT NULL,
    test_period TEXT NOT NULL,
    metrics JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO districts (name, state)
VALUES
    ('Kamrup', 'Assam'),
    ('Kamrup Metropolitan', 'Assam'),
    ('Dibrugarh', 'Assam')
ON CONFLICT (name) DO NOTHING;