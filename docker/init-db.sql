-- =============================================================================
-- Econojin - Initial Database Schema
-- Executed on first PostgreSQL container startup
-- =============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- =============================================================================
-- Users & Authentication
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(40),
    organization VARCHAR(255),
    role VARCHAR(40) DEFAULT 'farmer',
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Refresh Tokens
-- =============================================================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(512) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE
);

-- =============================================================================
-- Farms (with PostGIS spatial support)
-- =============================================================================
CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    area_ha DOUBLE PRECISION,
    soil_type VARCHAR(100),
    irrigation_type VARCHAR(100),
    geom geography(Point, 4326),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Spatial index on farms.geom
CREATE INDEX IF NOT EXISTS ix_farms_geom_gist ON farms USING GIST (geom);
CREATE INDEX IF NOT EXISTS ix_farms_lat_lon ON farms (latitude, longitude)
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_farms_user_id ON farms (user_id);

-- =============================================================================
-- Crops
-- =============================================================================
CREATE TABLE IF NOT EXISTS crops (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    variety VARCHAR(255),
    planting_method VARCHAR(80),
    row_spacing_cm DOUBLE PRECISION,
    plant_spacing_cm DOUBLE PRECISION,
    sowing_depth_cm DOUBLE PRECISION,
    seed_rate_kg_ha DOUBLE PRECISION,
    irrigation_method VARCHAR(80),
    irrigation_interval_days INTEGER,
    kc_mid DOUBLE PRECISION,
    fertilizer_n_kg_ha DOUBLE PRECISION,
    fertilizer_p_kg_ha DOUBLE PRECISION,
    fertilizer_k_kg_ha DOUBLE PRECISION,
    soil_ph_min DOUBLE PRECISION,
    soil_ph_max DOUBLE PRECISION,
    harvest_method VARCHAR(80),
    harvest_moisture_pct DOUBLE PRECISION,
    common_pests TEXT,
    common_diseases TEXT,
    care_notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_crops_farm_id ON crops (farm_id);

-- =============================================================================
-- Weather Records
-- =============================================================================
CREATE TABLE IF NOT EXISTS weather_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID REFERENCES farms(id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    temperature_min DOUBLE PRECISION,
    temperature_max DOUBLE PRECISION,
    precipitation_mm DOUBLE PRECISION,
    humidity_pct DOUBLE PRECISION,
    wind_speed_ms DOUBLE PRECISION,
    solar_radiation_mj_m2 DOUBLE PRECISION,
    source VARCHAR(100) DEFAULT 'open-meteo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (farm_id, record_date, source)
);

CREATE INDEX IF NOT EXISTS ix_weather_farm_date ON weather_records (farm_id, record_date);

-- =============================================================================
-- Simulation Runs
-- =============================================================================
CREATE TABLE IF NOT EXISTS simulation_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    farm_id UUID REFERENCES farms(id) ON DELETE SET NULL,
    crop_id UUID REFERENCES crops(id) ON DELETE SET NULL,
    run_type VARCHAR(100) NOT NULL,
    parameters JSONB DEFAULT '{}',
    results JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_sim_runs_user ON simulation_runs (user_id);
CREATE INDEX IF NOT EXISTS ix_sim_runs_status ON simulation_runs (status);
CREATE INDEX IF NOT EXISTS ix_sim_runs_created ON simulation_runs (created_at DESC);

-- =============================================================================
-- Audit Log
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_audit_user ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS ix_audit_action ON audit_logs (action);
CREATE INDEX IF NOT EXISTS ix_audit_created ON audit_logs (created_at DESC);

-- =============================================================================
-- Rate Limiting (PostgreSQL-backed)
-- =============================================================================
CREATE TABLE IF NOT EXISTS rate_limit_entries (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    count INTEGER DEFAULT 1,
    UNIQUE (key, window_start)
);

CREATE INDEX IF NOT EXISTS ix_rate_limit_key ON rate_limit_entries (key, window_start);

-- =============================================================================
-- Celery Task Results
-- =============================================================================
CREATE TABLE IF NOT EXISTS celery_taskmeta (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    result JSONB,
    date_done TIMESTAMPTZ,
    traceback TEXT,
    name VARCHAR(255),
    args JSONB,
    kwargs JSONB,
    worker VARCHAR(255),
    retries INTEGER DEFAULT 0,
    queue VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_celery_task_id ON celery_taskmeta (task_id);
CREATE INDEX IF NOT EXISTS ix_celery_status ON celery_taskmeta (status);

-- =============================================================================
-- Populate spatial geometry from lat/lon (trigger)
-- =============================================================================
CREATE OR REPLACE FUNCTION update_farm_geom()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.geom := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_farm_geom ON farms;
CREATE TRIGGER trg_farm_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON farms
    FOR EACH ROW
    EXECUTE FUNCTION update_farm_geom();

-- =============================================================================
-- Updated-at trigger helper
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated ON users;
CREATE TRIGGER trg_users_updated
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_farms_updated ON farms;
CREATE TRIGGER trg_farms_updated
    BEFORE UPDATE ON farms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

DROP TRIGGER IF EXISTS trg_crops_updated ON crops;
CREATE TRIGGER trg_crops_updated
    BEFORE UPDATE ON crops
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

COMMENT ON EXTENSION postgis IS 'Geospatial support for farm locations and spatial queries';
COMMENT ON EXTENSION pg_stat_statements IS 'Query performance monitoring';
