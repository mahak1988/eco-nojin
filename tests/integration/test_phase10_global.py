"""Final Integration Tests - Phase 10"""
import pytest
from datetime import datetime
from api.domains.training.services.training_service import TrainingService


def test_global_pilots_loaded():
    """تست بارگذاری ۱۲ پایلوت جهانی"""
    import json
    from pathlib import Path
    
    data_dir = Path("data/pilots")
    pilots = [
        "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
        "ouarzazate", "wadi_rum", "sahel_senegal", "ethiopian_highlands",
        "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"
    ]
    
    for pilot in pilots:
        pilot_file = data_dir / f"{pilot}.json"
        assert pilot_file.exists(), f"Pilot data file not found: {pilot}"
        
        with open(pilot_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "pilot_id" in data
        assert "country" in data
        assert "continent" in data
        assert "baseline_indicators" in data


def test_global_expansion_plan():
    """تست برنامه گسترش بین‌المللی"""
    import json
    from pathlib import Path
    
    expansion_file = Path("data/global_expansion/regional_expansion_plan.json")
    assert expansion_file.exists()
    
    with open(expansion_file, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    assert "phase_1_mena" in plan
    assert "phase_2_sub_saharan_africa" in plan
    assert "phase_3_central_asia" in plan


def test_training_system():
    """تست سیستم آموزش"""
    service = TrainingService()
    
    assert len(service.modules) > 0
    
    # تست ماژول‌های بین‌المللی
    ouarzazate_modules = service.get_modules_by_pilot("ouarzazate")
    assert len(ouarzazate_modules) > 0
    
    rajasthan_modules = service.get_modules_by_pilot("rajasthan")
    assert len(rajasthan_modules) > 0
