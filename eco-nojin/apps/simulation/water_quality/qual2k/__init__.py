"""QUAL2K Wrapper for Eco Nozhin"""
import logging

logger = logging.getLogger(__name__)
from .wqi_calculator import WaterQualityIndex
from .wrapper import QUAL2KOutput, QUAL2KWrapper

__all__ = ["QUAL2KWrapper", "QUAL2KOutput", "WaterQualityIndex"]
