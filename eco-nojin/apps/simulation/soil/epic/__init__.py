"""EPIC Wrapper for Eco Nozhin"""
import logging

logger = logging.getLogger(__name__)
from .soil_productivity import SoilProductivityModel
from .wrapper import EPICOutput, EPICWrapper

__all__ = ["EPICWrapper", "EPICOutput", "SoilProductivityModel"]
