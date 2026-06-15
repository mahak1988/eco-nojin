"""
Pytest configuration and fixtures for Econojin tests.
This file ensures that the 'api' package is importable from tests.
"""
import os
import sys
from pathlib import Path

# ========================================================================
# CRITICAL: Add project root to sys.path so 'api' package is importable
# ========================================================================
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Also set PYTHONPATH environment variable for subprocess compatibility
os.environ.setdefault('PYTHONPATH', str(PROJECT_ROOT))

# ========================================================================
# Now we can safely import from api
# ========================================================================
try:
    from api.core.config import settings
    from api.core.database import engine, Base, get_db
    from sqlalchemy.orm import Session
    import pytest
    from fastapi.testclient import TestClient
    from api.main import app
    
    @pytest.fixture(scope="session")
    def test_settings():
        """Fixture for test settings"""
        return settings
    
    @pytest.fixture(scope="session")
    def test_engine():
        """Fixture for test database engine"""
        return engine
    
    @pytest.fixture(scope="function")
    def db_session():
        """Fixture for database session with automatic rollback"""
        connection = engine.connect()
        transaction = connection.begin()
        session = Session(bind=connection)
        
        yield session
        
        session.close()
        transaction.rollback()
        connection.close()
    
    @pytest.fixture(scope="function")
    def client(db_session: Session):
        """Fixture for FastAPI test client with database override"""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as test_client:
            yield test_client
        app.dependency_overrides.clear()
    
    @pytest.fixture(scope="session", autouse=True)
    def setup_test_database():
        """Setup test database tables once per test session"""
        # Import all models to ensure they're registered with Base
        try:
            from api.domains.dashboard.models import db_models as dashboard_models
            from api.domains.hydrology.models import db_models as hydrology_models
            from api.domains.iot.models import db_models as iot_models
            from api.domains.logframe.models import db_models as logframe_models
            from api.domains.mrv.models import db_models as mrv_models
            from api.domains.pilots.models import db_models as pilots_models
            from api.domains.psychology.models import db_models as psychology_models
            from api.domains.remote_sensing.models import db_models as remote_sensing_models
            from api.domains.safeguards.models import db_models as safeguards_models
            from api.domains.training.models import db_models as training_models
            from api.domains.lms.models import db_models as lms_models
            from api.domains.drought.models import db_models as drought_models
            from api.domains.soil_water.models import db_models as soil_water_models
            from api.domains.financial.models import db_models as financial_models
        except ImportError as e:
            print(f"Warning: Could not import some db_models: {e}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        yield
        # Optional: Drop all tables after tests
        # Base.metadata.drop_all(bind=engine)

except ImportError as e:
    print(f"Warning: Could not set up full test fixtures: {e}")
    print("Basic tests will still run, but database fixtures may not be available.")
    
    # Provide minimal pytest setup
    import pytest
    
    @pytest.fixture(scope="session")
    def project_root():
        """Fixture for project root path"""
        return PROJECT_ROOT
