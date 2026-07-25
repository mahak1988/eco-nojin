"""WEAP Model Wrapper for Eco Nozhin"""
import logging

logger = logging.getLogger(__name__)
from .wrapper import WEAPWrapper, WEAPOutput, WEAPScenario

__all__ = ["WEAPWrapper", "WEAPOutput", "WEAPScenario"]
