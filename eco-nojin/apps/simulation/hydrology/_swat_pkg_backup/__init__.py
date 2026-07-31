"""SWAT Model Wrapper for Eco Nozhin"""
import logging

logger = logging.getLogger(__name__)
from .wrapper import SWATOutput, SWATWrapper

__all__ = ["SWATWrapper", "SWATOutput"]
