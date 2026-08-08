# simulation | Comprehensive Simulation Module for Econojin

> **Note:** This module is the **simulation core** of the Econojin platform.
> It includes 28+ specialized simulators across climate, agriculture, economics, energy,
> water, soil, biodiversity, carbon, and ecosystem services domains.

## Responsibilities

This module has six main responsibilities:

1. **28+ Specialized Simulators** — Modeling across environmental and economic domains
2. **Simulator Registration** (`registry.py`) — Automatic registration via decorators
3. **Simulation Chain** (`chain/`) — Chained simulator execution (output→input)
4. **Report Generation** (`reports/`) — CSV/JSON report generation from simulation results
5. **Validation** (`validation/`) — Input and output data validation
6. **Simulation API** (`router.py`) — Run, monitor, and manage simulations

## Structure

```
simulation/
├── __init__.py                # Module init
├── base.py                    # ★ Simulator base class
├── registry.py                # ★ Automatic simulator registration
├── router.py                  # ★ FastAPI router
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic
├── repository.py              # Database access
├── models.py                  # ORM models
├── dependencies.py            # FastAPI dependencies
│
├── climate/                   # ★ Climate simulators
├── agriculture/               # ★ Agriculture simulators
├── economics/                 # ★ Economics simulators
├── energy/                    # ★ Energy simulators
├── hydrology/                 # ★ Hydrology simulators
├── soil/                      # ★ Soil simulators
├── biodiversity/              # ★ Biodiversity simulators
├── carbon_cycle/              # ★ Carbon cycle simulators
├── ecosystem_services/        # ★ Ecosystem services simulators
├── water_quality/             # ★ Water quality simulators
├── urban/                     # ★ Urban simulators
├── earth_engine/              # ★ Earth engine simulators
│
├── chain/                     # ★ Simulation chain
│   ├── router.py              #   Chain API
│   └── ...
├── reports/                   # ★ Report generation
│   ├── router.py              #   Report API
│   └── ...
├── validation/                # ★ Validation
├── data/                      # ★ Simulation data
├── runs/                      # ★ Run results
├── advisory/                  # ★ Smart advisory
└── tests/                     # Pytest tests
```

## Simulator Base Class (`base.py`)

All simulators inherit from the `Simulator` base class:

```python
from simulation.base import Simulator


class MySimulator(Simulator):
    """Custom simulator"""

    name = "my_simulator"
    description = "Simulator description"
    inputs = [{"name": "param1", "type": "float", "description": "..."}]
    outputs = [{"name": "result1", "type": "float", "description": "..."}]

    async def run(self, inputs: dict) -> dict:
        # Simulation logic
        return {"result1": 42.0}
```

## Automatic Registration (`registry.py`)

Simulators are registered automatically using the `@register_simulator` decorator:

```python
from simulation.registry import register_simulator


@register_simulator
class ClimateModel(Simulator):
    name = "climate_model"
    ...
```

## 28+ Specialized Simulators

### 🌤️ Climate
| Simulator | Description |
|----------|--------|
| `climate_model` | Climate change modeling |
| `weather_generator` | Weather data generation |
| `precipitation` | Precipitation simulation |
| `temperature` | Temperature simulation |

### 🌾 Agriculture
| Simulator | Description |
|----------|--------|
| `crop_growth` | Crop growth simulation |
| `irrigation` | Irrigation management |
| `yield_prediction` | Crop yield prediction |
| `pest_dynamics` | Pest population dynamics |

### 💰 Economics
| Simulator | Description |
|----------|--------|
| `market_model` | Market and price modeling |
| `supply_chain` | Supply chain analysis |
| `cost_benefit` | Cost-benefit analysis |

### ⚡ Energy
| Simulator | Description |
|----------|--------|
| `renewable_potential` | Renewable energy potential |
| `energy_demand` | Energy demand forecasting |
| `grid_optimization` | Power grid optimization |

### 💧 Hydrology
| Simulator | Description |
|----------|--------|
| `watershed_model` | Watershed modeling |
| `groundwater` | Groundwater simulation |
| `reservoir` | Reservoir management |

### 🌱 Soil
| Simulator | Description |
|----------|--------|
| `soil_carbon` | Soil organic carbon |
| `erosion` | Soil erosion |
| `nutrient_cycle` | Nutrient cycling |

### 🦋 Biodiversity
| Simulator | Description |
|----------|--------|
| `species_distribution` | Species distribution modeling |
| `habitat_suitability` | Habitat suitability assessment |
| `population_dynamics` | Population dynamics |

### 🌍 Carbon Cycle
| Simulator | Description |
|----------|--------|
| `carbon_flux` | Carbon flux modeling |
| `sequestration` | Carbon sequestration |
| `emissions` | Greenhouse gas emissions |

### 🏙️ Urban
| Simulator | Description |
|----------|--------|
| `urban_heat` | Urban heat island effect |
| `land_use` | Land use change |
| `green_infrastructure` | Green infrastructure planning |

## API Endpoints

### Simulation

| Method | Path | Description |
|--------|------|--------|
| POST | `/api/v1/simulation/run` | Execute simulation |
| GET | `/api/v1/simulation/runs` | List previous runs |
| GET | `/api/v1/simulation/runs/{id}` | Run details |
| GET | `/api/v1/simulation/simulators` | List available simulators |

**Execute Simulation:**
```json
// POST /api/v1/simulation/run
{
    "simulator": "climate_model",
    "inputs": {
        "temperature": 1.5,
        "precipitation": -10,
        "years": 50
    },
    "chain": ["climate_model", "crop_growth", "market_model"]
}
```

### Simulation Chain

| Method | Path | Description |
|--------|------|--------|
| POST | `/api/v1/simulation/chain/run` | Execute simulator chain |
| GET | `/api/v1/simulation/chain/chains` | List defined chains |

### Reports

| Method | Path | Description |
|--------|------|--------|
| GET | `/api/v1/simulation/reports/csv` | CSV output |
| GET | `/api/v1/simulation/reports/json` | JSON output |

## Development & Testing

```bash
# From project root
cd d:\econojin.com

# Run tests
pytest apps/simulation/tests/ -v

# Test a specific simulator
pytest apps/simulation/tests/test_climate.py -v

# Run development server
python apps/main.py
# or
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## Changelog

- **Phase 2:** Full rewrite with base simulator architecture (`base.py`)
- **Phase 2:** Added 28+ specialized simulators across 11 domains
- **Phase 2:** Automatic registration system with decorators (`registry.py`)
- **Phase 2:** Simulation chain (output of one simulator → input of next)
- **Phase 2:** CSV/JSON report generation
- **Phase 2:** Input/output validation
