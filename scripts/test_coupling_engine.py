#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test coupling engine"""

import pytest
from backend.services.coupling_engine import CouplingConfig, CouplingEngine, CouplingError


class MockModel:
    """Mock model for testing"""

    def __init__(self, name):
        self.name = name

    def run(self, inputs):
        """Mock run method"""
        return {"model": self.name, "result": "success", "output": inputs.get("value", 0) * 2}


class TestCouplingEngine:
    """Test coupling engine"""

    def test_instantiation(self):
        """Test CouplingEngine can be instantiated"""
        engine = CouplingEngine()
        assert engine is not None
        assert isinstance(engine.config, CouplingConfig)

    def test_has_run_method(self):
        """Test CouplingEngine has run method"""
        engine = CouplingEngine()
        assert hasattr(engine, "run")
        assert callable(engine.run)

    def test_configuration(self):
        """Test CouplingEngine configuration"""
        config = {
            "models": ["model1", "model2"],
            "coupling_strategy": "sequential",
            "max_iterations": 20,
            "tolerance": 0.05,
            "enable_logging": True,
        }

        engine = CouplingEngine(config)

        assert engine.config.models == ["model1", "model2"]
        assert engine.config.coupling_strategy == "sequential"
        assert engine.config.max_iterations == 20
        assert engine.config.tolerance == 0.05
        assert engine.config.enable_logging is True

    def test_empty_input(self):
        """Test CouplingEngine with empty input"""
        engine = CouplingEngine()
        result = engine.run({})

        assert result["status"] == "success"
        assert result["results"] == {}
        assert result["models_executed"] == []

    def test_register_model(self):
        """Test registering models"""
        engine = CouplingEngine({"enable_logging": True})
        model = MockModel("test_model")

        engine.register_model("test", model)

        assert "test" in engine._models
        assert engine._models["test"] == model

    def test_run_with_models(self):
        """Test running with registered models"""
        engine = CouplingEngine(
            {
                "models": ["model1", "model2"],
                "coupling_strategy": "sequential",
                "enable_logging": True,
            }
        )

        # Register models
        engine.register_model("model1", MockModel("model1"))
        engine.register_model("model2", MockModel("model2"))

        # Run engine
        result = engine.run({"value": 5})

        assert result["status"] == "success"
        assert "model1" in result["results"]
        assert "model2" in result["results"]
        assert result["execution_time"] >= 0

    def test_execution_log(self):
        """Test execution logging"""
        engine = CouplingEngine({"enable_logging": True})

        # Register model
        engine.register_model("test", MockModel("test"))

        # Check log
        log = engine.get_execution_log()
        assert len(log) == 1
        assert log[0]["action"] == "register_model"
        assert log[0]["model"] == "test"

    def test_clear_log(self):
        """Test clearing execution log"""
        engine = CouplingEngine({"enable_logging": True})
        engine.register_model("test", MockModel("test"))

        # Clear log
        engine.clear_log()

        # Check log is empty
        log = engine.get_execution_log()
        assert len(log) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
