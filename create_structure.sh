#!/bin/bash

BASE="apps/api"

# ======================== ایجاد پوشه‌ها ========================
mkdir -p $BASE/app/core
mkdir -p $BASE/app/domain/hydrology
mkdir -p $BASE/app/domain/soil
mkdir -p $BASE/app/domain/carbon
mkdir -p $BASE/app/domain/drought
mkdir -p $BASE/app/domain/ecosystem
mkdir -p $BASE/app/domain/energy
mkdir -p $BASE/app/domain/biodiversity
mkdir -p $BASE/app/domain/common

mkdir -p $BASE/app/application/hydrology
mkdir -p $BASE/app/application/soil
mkdir -p $BASE/app/application/carbon
mkdir -p $BASE/app/application/common

mkdir -p $BASE/app/infrastructure/persistence/repositories
mkdir -p $BASE/app/infrastructure/persistence/models
mkdir -p $BASE/app/infrastructure/external_services/weather
mkdir -p $BASE/app/infrastructure/external_services/satellite
mkdir -p $BASE/app/infrastructure/external_services/soil_data
mkdir -p $BASE/app/infrastructure/messaging

mkdir -p $BASE/app/presentation/api/v1/endpoints
mkdir -p $BASE/app/presentation/api/v1/schemas
mkdir -p $BASE/app/presentation/middleware

mkdir -p $BASE/app/scientific/hydrology/swat
mkdir -p $BASE/app/scientific/hydrology/modflow
mkdir -p $BASE/app/scientific/hydrology/hechms
mkdir -p $BASE/app/scientific/hydrology/hecras
mkdir -p $BASE/app/scientific/hydrology/hbv
mkdir -p $BASE/app/scientific/hydrology/mike_she
mkdir -p $BASE/app/scientific/hydrology/hspf
mkdir -p $BASE/app/scientific/hydrology/vic
mkdir -p $BASE/app/scientific/hydrology/topmodel
mkdir -p $BASE/app/scientific/hydrology/sacramento
mkdir -p $BASE/app/scientific/hydrology/qual2k
mkdir -p $BASE/app/scientific/hydrology/wasp

mkdir -p $BASE/app/scientific/soil/hydrus
mkdir -p $BASE/app/scientific/soil/rusle2
mkdir -p $BASE/app/scientific/soil/wepp

mkdir -p $BASE/app/scientific/carbon/rothc
mkdir -p $BASE/app/scientific/carbon/co2fix
mkdir -p $BASE/app/scientific/carbon/century

mkdir -p $BASE/app/scientific/drought

mkdir -p $BASE/app/scientific/ecosystem/invest
mkdir -p $BASE/app/scientific/ecosystem/aries
mkdir -p $BASE/app/scientific/ecosystem/teeb
mkdir -p $BASE/app/scientific/ecosystem/costing_nature

mkdir -p $BASE/app/scientific/energy/leap
mkdir -p $BASE/app/scientific/energy/homer
mkdir -p $BASE/app/scientific/energy/energyplan

mkdir -p $BASE/app/scientific/biodiversity/maxent
mkdir -p $BASE/app/scientific/biodiversity/itree

mkdir -p $BASE/app/scientific/common

mkdir -p $BASE/tests/unit/domain
mkdir -p $BASE/tests/unit/application
mkdir -p $BASE/tests/unit/scientific
mkdir -p $BASE/tests/integration
mkdir -p $BASE/tests/e2e

mkdir -p $BASE/scripts
mkdir -p $BASE/migrations/versions
mkdir -p $BASE/docs

# ======================== ایجاد فایل‌های __init__.py ========================
# ایجاد __init__.py در تمام پوشه‌های اصلی و زیرپوشه‌ها
find $BASE -type d -exec touch {}/__init__.py \;

# ======================== ایجاد فایل‌های اصلی (جای خالی) ========================

# Core
touch $BASE/app/main.py
touch $BASE/app/core/config.py
touch $BASE/app/core/database.py
touch $BASE/app/core/security.py
touch $BASE/app/core/deps.py
touch $BASE/app/core/exceptions.py

# Domain - هر دامنه
for domain in hydrology soil carbon drought ecosystem energy biodiversity; do
    touch $BASE/app/domain/$domain/entities.py
    touch $BASE/app/domain/$domain/value_objects.py
    touch $BASE/app/domain/$domain/repositories.py
    touch $BASE/app/domain/$domain/services.py
    if [ $domain == "hydrology" ]; then
        touch $BASE/app/domain/$domain/events.py   # فقط هیدرولوژی events داشت
    fi
done

# Domain common
touch $BASE/app/domain/common/base_entity.py
touch $BASE/app/domain/common/base_repository.py

# Application
touch $BASE/app/application/hydrology/run_simulation.py
touch $BASE/app/application/hydrology/get_results.py
touch $BASE/app/application/hydrology/dto.py
touch $BASE/app/application/soil/analyze_soil.py
touch $BASE/app/application/soil/dto.py
touch $BASE/app/application/carbon/calculate_sequestration.py
touch $BASE/app/application/carbon/dto.py
touch $BASE/app/application/common/base_use_case.py

# Infrastructure
touch $BASE/app/infrastructure/persistence/repositories/hydrology_repository.py
touch $BASE/app/infrastructure/persistence/repositories/soil_repository.py
touch $BASE/app/infrastructure/persistence/repositories/carbon_repository.py
touch $BASE/app/infrastructure/persistence/models/hydrology.py
touch $BASE/app/infrastructure/persistence/models/soil.py
touch $BASE/app/infrastructure/persistence/models/carbon.py

touch $BASE/app/infrastructure/external_services/weather/open_meteo.py
touch $BASE/app/infrastructure/external_services/weather/weather_api.py
touch $BASE/app/infrastructure/external_services/satellite/sentinel.py
touch $BASE/app/infrastructure/external_services/satellite/landsat.py
touch $BASE/app/infrastructure/external_services/satellite/modis.py
touch $BASE/app/infrastructure/external_services/soil_data/soilgrids.py

touch $BASE/app/infrastructure/messaging/email_service.py
touch $BASE/app/infrastructure/messaging/notification_service.py

# Presentation
touch $BASE/app/presentation/api/v1/router.py
for endpoint in hydrology soil carbon drought ecosystem energy biodiversity auth users health; do
    touch $BASE/app/presentation/api/v1/endpoints/$endpoint.py
done
touch $BASE/app/presentation/api/v1/schemas/hydrology.py
touch $BASE/app/presentation/api/v1/schemas/soil.py
touch $BASE/app/presentation/api/v1/schemas/carbon.py
touch $BASE/app/presentation/api/v1/schemas/common.py
touch $BASE/app/presentation/api/dependencies.py
touch $BASE/app/presentation/middleware/authentication.py
touch $BASE/app/presentation/middleware/authorization.py
touch $BASE/app/presentation/middleware/rate_limit.py
touch $BASE/app/presentation/middleware/logging.py

# Scientific - hydrology models
touch $BASE/app/scientific/hydrology/swat/wrapper.py
touch $BASE/app/scientific/hydrology/swat/config_manager.py
touch $BASE/app/scientific/hydrology/swat/output_parser.py
touch $BASE/app/scientific/hydrology/modflow/wrapper.py
touch $BASE/app/scientific/hydrology/modflow/model_builder.py
touch $BASE/app/scientific/hydrology/hechms/wrapper.py
touch $BASE/app/scientific/hydrology/hechms/engine.py
touch $BASE/app/scientific/hydrology/hechms/models.py
touch $BASE/app/scientific/hydrology/hechms/loss_methods.py
touch $BASE/app/scientific/hydrology/hechms/routing_methods.py
touch $BASE/app/scientific/hydrology/hechms/transform_methods.py
touch $BASE/app/scientific/hydrology/hechms/baseflow.py
touch $BASE/app/scientific/hydrology/hechms/validation.py
touch $BASE/app/scientific/hydrology/hecras/wrapper.py
touch $BASE/app/scientific/hydrology/hecras/models.py
touch $BASE/app/scientific/hydrology/hecras/flood_analyzer.py
for model in hbv mike_she hspf vic topmodel sacramento qual2k wasp; do
    touch $BASE/app/scientific/hydrology/$model/models.py
    touch $BASE/app/scientific/hydrology/$model/services.py
    # بعضی wrapper هم دارند
    if [ $model != "hbv" ] && [ $model != "topmodel" ]; then
        touch $BASE/app/scientific/hydrology/$model/wrapper.py
    fi
done

# Scientific - soil
touch $BASE/app/scientific/soil/hydrus/wrapper.py
touch $BASE/app/scientific/soil/rusle2/wrapper.py
touch $BASE/app/scientific/soil/wepp/wrapper.py
touch $BASE/app/scientific/soil/soil_parameters.py

# Scientific - carbon
touch $BASE/app/scientific/carbon/rothc/wrapper.py
touch $BASE/app/scientific/carbon/rothc/decomposition.py
touch $BASE/app/scientific/carbon/rothc/verification.py
touch $BASE/app/scientific/carbon/co2fix/wrapper.py
touch $BASE/app/scientific/carbon/co2fix/tree_growth.py
touch $BASE/app/scientific/carbon/co2fix/wood_products.py
touch $BASE/app/scientific/carbon/century/wrapper.py

# Scientific - drought
touch $BASE/app/scientific/drought/spei.py
touch $BASE/app/scientific/drought/chirps.py
touch $BASE/app/scientific/drought/drought_indices.py

# Scientific - ecosystem
touch $BASE/app/scientific/ecosystem/invest/wrapper.py
touch $BASE/app/scientific/ecosystem/invest/carbon_model.py
touch $BASE/app/scientific/ecosystem/invest/water_yield_model.py
touch $BASE/app/scientific/ecosystem/invest/habitat_quality.py
touch $BASE/app/scientific/ecosystem/invest/sediment_model.py
touch $BASE/app/scientific/ecosystem/invest/pollination_model.py
touch $BASE/app/scientific/ecosystem/aries/wrapper.py
touch $BASE/app/scientific/ecosystem/aries/bayesian_network.py
touch $BASE/app/scientific/ecosystem/teeb/wrapper.py
touch $BASE/app/scientific/ecosystem/teeb/valuation_methods.py
touch $BASE/app/scientific/ecosystem/teeb/natural_capital_accounting.py
touch $BASE/app/scientific/ecosystem/costing_nature/wrapper.py

# Scientific - energy
touch $BASE/app/scientific/energy/leap/wrapper.py
touch $BASE/app/scientific/energy/leap/energy_scenarios.py
touch $BASE/app/scientific/energy/homer/wrapper.py
touch $BASE/app/scientific/energy/homer/energy_resources.py
touch $BASE/app/scientific/energy/energyplan/wrapper.py

# Scientific - biodiversity
touch $BASE/app/scientific/biodiversity/maxent/wrapper.py
touch $BASE/app/scientific/biodiversity/maxent/species_database.py
touch $BASE/app/scientific/biodiversity/itree/wrapper.py
touch $BASE/app/scientific/biodiversity/itree/ecosystem_services.py

# Scientific - common
touch $BASE/app/scientific/common/base_wrapper.py
touch $BASE/app/scientific/common/data_transformer.py
touch $BASE/app/scientific/common/validation.py

# Tests
touch $BASE/tests/conftest.py
touch $BASE/tests/unit/domain/test_hydrology.py
touch $BASE/tests/unit/domain/test_soil.py
touch $BASE/tests/unit/domain/test_carbon.py
touch $BASE/tests/unit/application/test_hydrology_use_cases.py
touch $BASE/tests/unit/application/test_soil_use_cases.py
touch $BASE/tests/unit/scientific/test_swat_wrapper.py
touch $BASE/tests/unit/scientific/test_modflow_wrapper.py
touch $BASE/tests/unit/scientific/test_rothc_wrapper.py
touch $BASE/tests/integration/test_api_endpoints.py
touch $BASE/tests/integration/test_database.py
touch $BASE/tests/integration/test_scientific_integration.py
touch $BASE/tests/e2e/test_full_workflow.py

# Scripts, migrations, docs
touch $BASE/scripts/seed_data.py
touch $BASE/scripts/seed_admin.py
touch $BASE/scripts/reset_db.py
touch $BASE/migrations/alembic.ini
touch $BASE/migrations/env.py
touch $BASE/docs/api.md
touch $BASE/docs/architecture.md
touch $BASE/docs/scientific_models.md

# Root config files
touch $BASE/pyproject.toml
touch $BASE/requirements.txt
touch $BASE/requirements-dev.txt
touch $BASE/README.md
touch $BASE/.env.example

echo "✅ ساختار کامل پروژه در '$BASE' ایجاد شد."