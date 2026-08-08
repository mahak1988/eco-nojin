"""WEAP Model Wrapper for Eco Nozhin"""

import logging

logger = logging.getLogger(__name__)
from .wrapper import WEAPOutput, WEAPScenario, WEAPWrapper

__all__ = ["WEAPOutput", "WEAPScenario", "WEAPWrapper"]
