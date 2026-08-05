"""
Tests for apps/regional module (Phase 1 regional foundation).
Trilingual error detail keys are validated where applicable.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from apps.regional.schemas import (
    BioFertilizerCreate,
    CountryProfileCreate,
    SoilTypeCreate,
)
from apps.regional.service import SEED_BIOFERTILIZERS, SEED_COUNTRIES, SEED_SOILS


def test_seed_countries_have_trilingual_names():
    assert len(SEED_COUNTRIES) >= 5
    for c in SEED_COUNTRIES:
        assert c["name_en"]
        assert c["name_fa"]
        assert c["name_ar"]
        assert c["iso_code"]
        assert "opportunities" in c
        assert "en" in c["opportunities"]
        assert "fa" in c["opportunities"]
        assert "ar" in c["opportunities"]


def test_seed_soils_trilingual():
    assert len(SEED_SOILS) >= 2
    for s in SEED_SOILS:
        assert s["name_en"]
        assert s["name_fa"]
        assert s["name_ar"]
        assert s["texture"]


def test_seed_biofertilizers_trilingual():
    assert len(SEED_BIOFERTILIZERS) >= 3
    for b in SEED_BIOFERTILIZERS:
        assert b["name_en"]
        assert b["name_fa"]
        assert b["name_ar"]
        assert b["fertilizer_type"]
        assert "benefits" in b
        assert "en" in b["benefits"]


def test_country_profile_schema_validation():
    data = CountryProfileCreate(
        iso_code="IRN",
        iso2="IR",
        name_en="Iran",
        name_fa="ایران",
        name_ar="إيران",
        priority="critical",
    )
    assert data.iso_code == "IRN"
    assert data.priority == "critical"


def test_soil_type_schema_validation():
    data = SoilTypeCreate(
        code="TEST-LOAM",
        name_en="Test loam",
        name_fa="لوم آزمایشی",
        name_ar="طمي تجريبي",
        texture="loam",
    )
    assert data.texture == "loam"


def test_biofertilizer_schema_validation():
    data = BioFertilizerCreate(
        code="BF-TEST",
        name_en="Test BF",
        name_fa="کود آزمایشی",
        name_ar="سماد تجريبي",
        fertilizer_type="nitrogen_fixing",
        drought_tolerance="high",
    )
    assert data.drought_tolerance == "high"


def test_country_priority_pattern():
    with pytest.raises(ValidationError):
        CountryProfileCreate(
            iso_code="XXX",
            iso2="XX",
            name_en="X",
            name_fa="X",
            name_ar="X",
            priority="invalid",
        )
