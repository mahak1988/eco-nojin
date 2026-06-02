"""
Fallback implementation for AquaCrop when the package is not installed.
This provides mock classes to prevent import errors.
"""

class AquaCropOS:
    """Mock AquaCropOS class"""
    def __init__(self, *args, **kwargs):
        raise ImportError(
            "AquaCrop is not installed. Please install with: "
            "pip install aquacrop -i https://mirror-pypi.runflare.com/simple/"
        )

class CropParameters:
    """Mock CropParameters class"""
    def __init__(self, *args, **kwargs):
        pass

class SoilParameters:
    """Mock SoilParameters class"""
    def __init__(self, *args, **kwargs):
        pass

class ClimateData:
    """Mock ClimateData class"""
    def __init__(self, *args, **kwargs):
        pass
