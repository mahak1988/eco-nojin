"""
Import all models for database initialization
"""

# Core Models
from api.models.project import Project

# Auth & User
from api.modules.auth import models as auth_models

# Farmer
from api.modules.farmer import models as farmer_models

# EcoCoin & Blockchain
from api.modules.ecocoin import models as ecocoin_models

# Environmental
from api.modules.soil_water import models as soil_water_models
from api.modules.soil_water import erosion_models
from api.modules.soil import models as soil_models
from api.modules.iot import models as iot_models
from api.modules.mrv import models as mrv_models

# Business
from api.modules.store import models as store_models
from api.modules.financial import models as financial_models
from api.modules.accounting import models as accounting_models

# Content & Community
from api.modules.academy import models as academy_models
from api.modules.library import models as library_models
from api.modules.community import models as community_models
from api.modules.newsletter import models as newsletter_models
from api.modules.psychology import models as psychology_models
from api.modules.games import models as games_models
from api.modules.calendar import models as calendar_models

# Operations
from api.modules.maintenance import models as maintenance_models

__all__ = [
    "Project",
    "auth_models",
    "farmer_models",
    "ecocoin_models",
    "soil_water_models",
    "erosion_models",
    "soil_models",
        "iot_models",
    "mrv_models",
    "store_models",
    "financial_models",
    "accounting_models",
    "academy_models",
    "library_models",
    "community_models",
    "newsletter_models",
    "psychology_models",
    "games_models",
    "calendar_models",
    "maintenance_models",
]
