"""WASP Wrapper for Eco Nozhin"""
import logging

logger = logging.getLogger(__name__)
from .eutrophication_model import EutrophicationModel
from .wrapper import WASPOutput, WASPWrapper

__all__ = ["WASPWrapper", "WASPOutput", "EutrophicationModel"]
