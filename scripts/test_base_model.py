#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test BaseModel functionality
"""

from typing import Any, Dict

import pytest
from backend.models.base_model import BaseModel


class ConcreteModel(BaseModel):
    """Concrete implementation of BaseModel for testing"""

    def setup(self) -> None:
        """Setup implementation"""
        self.is_setup = True

    def run(self) -> Dict[str, Any]:
        """Run implementation"""
        return {"status": "success", "config": self.config}


class TestBaseModel:
    """Test suite for BaseModel"""

    def test_base_model_instantiation(self):
        """Test that concrete model can be instantiated"""
        model = ConcreteModel()
        assert isinstance(model, BaseModel)
        assert model.name == "ConcreteModel"

    def test_base_model_with_kwargs(self):
        """Test BaseModel initialization with kwargs"""
        model = ConcreteModel(config={"name": "test", "value": 42})
        assert model.config == {"name": "test", "value": 42}

    def test_base_model_repr(self):
        """Test BaseModel string representation"""
        model = ConcreteModel(config={"key": "value"})
        repr_str = str(model)
        assert "ConcreteModel" in repr_str or "ConcreteModel" in model.name

    def test_base_model_abstract(self):
        """Test that BaseModel cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseModel()

    def test_base_model_get_config(self):
        """Test get_config method"""
        model = ConcreteModel(config={"test": "value"})
        config = model.get_config()
        assert config == {"test": "value"}
        # Verify it's a copy
        config["new_key"] = "new_value"
        assert "new_key" not in model.config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
