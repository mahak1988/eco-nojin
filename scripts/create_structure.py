import os
from pathlib import Path

BASE = Path("apps/api")

# Define all directories
directories = [
    "app/core",
    "app/domain/hydrology",
    "app/domain/soil",
    "app/domain/carbon",
    "app/domain/drought",
    "app/domain/ecosystem",
    "app/domain/energy",
    "app/domain/biodiversity",
    "app/domain/common",
    "app/application/hydrology",
    "app/application/soil",
    "app/application/carbon",
    "app/application/common",
    "app/infrastructure/persistence/repositories",
    "app/infrastructure/persistence/models",
    "app/infrastructure/external_services/weather",
    "app/infrastructure/external_services/satellite",
    "app/infrastructure/external_services/soil_data",
    "app/infrastructure/messaging",
    "app/presentation/api/v1/endpoints",
    "app/presentation/api/v1/schemas",
    "app/presentation/middleware",
    # Scientific - hydrology
    "app/scientific/hydrology/swat",
    "app/scientific/hydrology/modflow",
    "app/scientific/hydrology/hechms",
    "app/scientific/hydrology/hecras",
    "app/scientific/hydrology/hbv",
    "app/scientific/hydrology/mike_she",
    "app/scientific/hydrology/hspf",
    "app/scientific/hydrology/vic",
    "app/scientific/hydrology/topmodel",
    "app/scientific/hydrology/sacramento",
    "app/scientific/hydrology/qual2k",
    "app/scientific/hydrology/wasp",
    # Scientific - soil
    "app/scientific/soil/hydrus",
    "app/scientific/soil/rusle2",
    "app/scientific/soil/wepp",
    # Scientific - carbon
    "app/scientific/carbon/rothc",
    "app/scientific/carbon/co2fix",
    "app/scientific/carbon/century",
    # Scientific - drought
    "app/scientific/drought",
    # Scientific - ecosystem
    "app/scientific/ecosystem/invest",
    "app/scientific/ecosystem/aries",
    "app/scientific/ecosystem/teeb",
    "app/scientific/ecosystem/costing_nature",
    # Scientific - energy
    "app/scientific/energy/leap",
    "app/scientific/energy/homer",
    "app/scientific/energy/energyplan",
    # Scientific - biodiversity
    "app/scientific/biodiversity/maxent",
    "app/scientific/biodiversity/itree",
    # Scientific - common
    "app/scientific/common",
    # Tests
    "tests/unit/domain",
    "tests/unit/application",
    "tests/unit/scientific",
    "tests/integration",
    "tests/e2e",
    # Scripts, migrations, docs
    "scripts",
    "migrations/versions",
    "docs",
]

# Create all directories with parents
for d in directories:
    (BASE / d).mkdir(parents=True, exist_ok=True)

# Function to touch files
def touch(*paths):
    for p in paths:
        (BASE / p).touch(exist_ok=True)

# Create __init__.py files in all directories (existing and new)
for dirpath, _, _ in os.walk(BASE):
    (Path(dirpath) / "__init__.py").touch(exist_ok=True)

# Core files
touch("app/main.py")
touch("app/core/config.py")
touch("app/core/database.py")
touch("app/core/security.py")
touch("app/core/deps.py")
touch("app/core/exceptions.py")

# Domain files
for domain in ["hydrology", "soil", "carbon", "drought", "ecosystem", "energy", "biodiversity"]:
    touch(f"app/domain/{domain}/entities.py")
    touch(f"app/domain/{domain}/value_objects.py")
    touch(f"app/domain/{domain}/repositories.py")
    touch(f"app/domain/{domain}/services.py")
    if domain == "hydrology":
        touch(f"app/domain/{domain}/events.py")

touch("app/domain/common/base_entity.py")
touch("app/domain/common/base_repository.py")

# Application files
touch("app/application/hydrology/run_simulation.py")
touch("app/application/hydrology/get_results.py")
touch("app/application/hydrology/dto.py")
touch("app/application/soil/analyze_soil.py")
touch("app/application/soil/dto.py")
touch("app/application/carbon/calculate_sequestration.py")
touch("app/application/carbon/dto.py")
touch("app/application/common/base_use_case.py")

# Infrastructure persistence
touch("app/infrastructure/persistence/repositories/hydrology_repository.py")
touch("app/infrastructure/persistence/repositories/soil_repository.py")
touch("app/infrastructure/persistence/repositories/carbon_repository.py")
touch("app/infrastructure/persistence/models/hydrology.py")
touch("app/infrastructure/persistence/models/soil.py")
touch("app/infrastructure/persistence/models/carbon.py")

# Infrastructure external services
touch("app/infrastructure/external_services/weather/open_meteo.py")
touch("app/infrastructure/external_services/weather/weather_api.py")
touch("app/infrastructure/external_services/satellite/sentinel.py")
touch("app/infrastructure/external_services/satellite/landsat.py")
touch("app/infrastructure/external_services/satellite/modis.py")
touch("app/infrastructure/external_services/soil_data/soilgrids.py")

# Messaging
touch("app/infrastructure/messaging/email_service.py")
touch("app/infrastructure/messaging/notification_service.py")

# Presentation API
touch("app/presentation/api/v1/router.py")
for endpoint in ["hydrology", "soil", "carbon", "drought", "ecosystem", "energy", "biodiversity", "auth", "users", "health"]:
    touch(f"app/presentation/api/v1/endpoints/{endpoint}.py")
touch("app/presentation/api/v1/schemas/hydrology.py")
touch("app/presentation/api/v1/schemas/soil.py")
touch("app/presentation/api/v1/schemas/carbon.py")
touch("app/presentation/api/v1/schemas/common.py")
touch("app/presentation/api/dependencies.py")

# Presentation middleware
touch("app/presentation/middleware/authentication.py")
touch("app/presentation/middleware/authorization.py")
touch("app/presentation/middleware/rate_limit.py")
touch("app/presentation/middleware/logging.py")

# Scientific - hydrology
touch("app/scientific/hydrology/swat/wrapper.py")
touch("app/scientific/hydrology/swat/config_manager.py")
touch("app/scientific/hydrology/swat/output_parser.py")
touch("app/scientific/hydrology/modflow/wrapper.py")
touch("app/scientific/hydrology/modflow/model_builder.py")
touch("app/scientific/hydrology/hechms/wrapper.py")
touch("app/scientific/hydrology/hechms/engine.py")
touch("app/scientific/hydrology/hechms/models.py")
touch("app/scientific/hydrology/hechms/loss_methods.py")
touch("app/scientific/hydrology/hechms/routing_methods.py")
touch("app/scientific/hydrology/hechms/transform_methods.py")
touch("app/scientific/hydrology/hechms/baseflow.py")
touch("app/scientific/hydrology/hechms/validation.py")
touch("app/scientific/hydrology/hecras/wrapper.py")
touch("app/scientific/hydrology/hecras/models.py")
touch("app/scientific/hydrology/hecras/flood_analyzer.py")

for model in ["hbv", "mike_she", "hspf", "vic", "topmodel", "sacramento", "qual2k", "wasp"]:
    touch(f"app/scientific/hydrology/{model}/models.py")
    touch(f"app/scientific/hydrology/{model}/services.py")
    if model not in ("hbv", "topmodel"):  # wrappers except hbv and topmodel
        touch(f"app/scientific/hydrology/{model}/wrapper.py")

# Scientific - soil
touch("app/scientific/soil/hydrus/wrapper.py")
touch("app/scientific/soil/rusle2/wrapper.py")
touch("app/scientific/soil/wepp/wrapper.py")
touch("app/scientific/soil/soil_parameters.py")

# Scientific - carbon
touch("app/scientific/carbon/rothc/wrapper.py")
touch("app/scientific/carbon/rothc/decomposition.py")
touch("app/scientific/carbon/rothc/verification.py")
touch("app/scientific/carbon/co2fix/wrapper.py")
touch("app/scientific/carbon/co2fix/tree_growth.py")
touch("app/scientific/carbon/co2fix/wood_products.py")
touch("app/scientific/carbon/century/wrapper.py")

# Scientific - drought
touch("app/scientific/drought/spei.py")
touch("app/scientific/drought/chirps.py")
touch("app/scientific/drought/drought_indices.py")

# Scientific - ecosystem
touch("app/scientific/ecosystem/invest/wrapper.py")
touch("app/scientific/ecosystem/invest/carbon_model.py")
touch("app/scientific/ecosystem/invest/water_yield_model.py")
touch("app/scientific/ecosystem/invest/habitat_quality.py")
touch("app/scientific/ecosystem/invest/sediment_model.py")
touch("app/scientific/ecosystem/invest/pollination_model.py")
touch("app/scientific/ecosystem/aries/wrapper.py")
touch("app/scientific/ecosystem/aries/bayesian_network.py")
touch("app/scientific/ecosystem/teeb/wrapper.py")
touch("app/scientific/ecosystem/teeb/valuation_methods.py")
touch("app/scientific/ecosystem/teeb/natural_capital_accounting.py")
touch("app/scientific/ecosystem/costing_nature/wrapper.py")

# Scientific - energy
touch("app/scientific/energy/leap/wrapper.py")
touch("app/scientific/energy/leap/energy_scenarios.py")
touch("app/scientific/energy/homer/wrapper.py")
touch("app/scientific/energy/homer/energy_resources.py")
touch("app/scientific/energy/energyplan/wrapper.py")

# Scientific - biodiversity
touch("app/scientific/biodiversity/maxent/wrapper.py")
touch("app/scientific/biodiversity/maxent/species_database.py")
touch("app/scientific/biodiversity/itree/wrapper.py")
touch("app/scientific/biodiversity/itree/ecosystem_services.py")

# Scientific common
touch("app/scientific/common/base_wrapper.py")
touch("app/scientific/common/data_transformer.py")
touch("app/scientific/common/validation.py")

# Tests
touch("tests/conftest.py")
touch("tests/unit/domain/test_hydrology.py")
touch("tests/unit/domain/test_soil.py")
touch("tests/unit/domain/test_carbon.py")
touch("tests/unit/application/test_hydrology_use_cases.py")
touch("tests/unit/application/test_soil_use_cases.py")
touch("tests/unit/scientific/test_swat_wrapper.py")
touch("tests/unit/scientific/test_modflow_wrapper.py")
touch("tests/unit/scientific/test_rothc_wrapper.py")
touch("tests/integration/test_api_endpoints.py")
touch("tests/integration/test_database.py")
touch("tests/integration/test_scientific_integration.py")
touch("tests/e2e/test_full_workflow.py")

# Scripts, migrations, docs
touch("scripts/seed_data.py")
touch("scripts/seed_admin.py")
touch("scripts/reset_db.py")
touch("migrations/alembic.ini")
touch("migrations/env.py")
touch("docs/api.md")
touch("docs/architecture.md")
touch("docs/scientific_models.md")

# Root config files
touch("pyproject.toml")
touch("requirements.txt")
touch("requirements-dev.txt")
touch("README.md")
touch(".env.example")

print("✅ ساختار کامل پروژه در 'apps/api' ایجاد شد.")