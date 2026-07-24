"""
Data Mapper for Multi-Model Simulations
========================================
Maps and transforms data between different model formats.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ModelDataMapping:
    """Definition of data mapping between models."""
    
    source_model: str
    target_model: str
    
    # Field mappings: {target_field: source_field}
    field_mappings: Dict[str, str] = field(default_factory=dict)
    
    # Transformation functions
    transformations: Dict[str, Callable] = field(default_factory=dict)
    
    # Default values for missing fields
    defaults: Dict[str, Any] = field(default_factory=dict)
    
    def apply(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mapping to source data."""
        result = {}
        
        for target_field, source_field in self.field_mappings.items():
            if source_field in source_data:
                value = source_data[source_field]
                
                # Apply transformation if defined
                if target_field in self.transformations:
                    value = self.transformations[target_field](value)
                
                result[target_field] = value
            elif target_field in self.defaults:
                result[target_field] = self.defaults[target_field]
        
        return result


class DataMapper:
    """
    Maps data between different simulation model formats.
    
    Handles conversion of outputs from one model to inputs for another,
    including unit conversions and format transformations.
    """
    
    def __init__(self):
        """Initialize data mapper with predefined mappings."""
        self.mappings: Dict[str, ModelDataMapping] = {}
        self._register_default_mappings()
        
        logger.info("DataMapper initialized")
    
    def _register_default_mappings(self):
        """Register common model-to-model mappings."""
        
        # SWAT -> RothC mapping
        swat_to_rothc = ModelDataMapping(
            source_model="swat",
            target_model="rothc",
            field_mappings={
                "soil_type": "soil_texture",
                "clay_content": "soil_clay_pct",
                "annual_rainfall": "precipitation_mm_year",
                "annual_temp_avg": "temperature_c_avg",
            },
            transformations={
                "clay_content": lambda x: x * 100 if x < 1 else x,  # fraction to percent
            },
            defaults={
                "soil_type": "loam",
                "clay_content": 25.0,
            }
        )
        self.mappings["swat->rothc"] = swat_to_rothc
        
        # APSIM -> RothC mapping
        apsim_to_rothc = ModelDataMapping(
            source_model="apsim",
            target_model="rothc",
            field_mappings={
                "crop_residue_input": "residue_biomass_kg_ha",
                "root_input": "root_biomass_kg_ha",
            },
            transformations={
                "crop_residue_input": lambda x: x / 1000.0,  # kg/ha to t/ha
                "root_input": lambda x: x / 1000.0,
            },
            defaults={
                "crop_residue_input": 3.0,
                "root_input": 1.5,
            }
        )
        self.mappings["apsim->rothc"] = apsim_to_rothc
        
        # DSSAT -> RothC mapping
        dssat_to_rothc = ModelDataMapping(
            source_model="dssat",
            target_model="rothc",
            field_mappings={
                "organic_carbon_input": "oc_addition_kg_ha",
            },
            transformations={
                "organic_carbon_input": lambda x: x / 1000.0,
            }
        )
        self.mappings["dssat->rothc"] = dssat_to_rothc
    
    def register_mapping(self, mapping: ModelDataMapping):
        """Register a custom mapping."""
        key = f"{mapping.source_model}->{mapping.target_model}"
        self.mappings[key] = mapping
        logger.info(f"Registered mapping: {key}")
    
    def map_data(
        self,
        source_model: str,
        target_model: str,
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map data from source model format to target model format.
        
        Args:
            source_model: Name of source model
            target_model: Name of target model
            source_data: Data in source model format
            
        Returns:
            Data in target model format
        """
        key = f"{source_model}->{target_model}"
        
        if key not in self.mappings:
            logger.warning(f"No mapping found for {key}, returning original data")
            return source_data
        
        mapping = self.mappings[key]
        result = mapping.apply(source_data)
        
        logger.debug(
            f"Mapped data from {source_model} to {target_model}: "
            f"{len(source_data)} -> {len(result)} fields"
        )
        
        return result
    
    def extract_shared_parameters(
        self,
        model_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract shared parameters from multiple model outputs.
        
        Args:
            model_outputs: Dictionary of {model_name: output_data}
            
        Returns:
            Dictionary of shared parameters
        """
        shared = {}
        
        # Extract common environmental parameters
        for model_name, output in model_outputs.items():
            if hasattr(output, 'to_dict'):
                output = output.to_dict()
            
            # Extract climate data
            if 'climate' in output:
                shared['climate'] = output['climate']
            
            # Extract soil data
            if 'soil' in output:
                shared['soil'] = output['soil']
        
        logger.info(f"Extracted {len(shared)} shared parameters")
        return shared
    
    def create_unified_dataset(
        self,
        model_outputs: Dict[str, Any],
        temporal_resolution: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Create unified time series dataset from multiple model outputs.
        
        Args:
            model_outputs: Dictionary of model outputs
            temporal_resolution: daily, monthly, yearly
            
        Returns:
            Unified dataset with aligned time series
        """
        unified = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "models_included": list(model_outputs.keys()),
                "temporal_resolution": temporal_resolution
            },
            "time_series": {},
            "aggregates": {}
        }
        
        # Merge time series from all models
        for model_name, output in model_outputs.items():
            if hasattr(output, 'to_dict'):
                output = output.to_dict()
            
            if 'time_series' in output or 'daily_outputs' in output:
                ts = output.get('time_series') or output.get('daily_outputs', [])
                
                for item in ts:
                    if 'date' in item:
                        date_key = item['date']
                        if date_key not in unified['time_series']:
                            unified['time_series'][date_key] = {}
                        
                        unified['time_series'][date_key][model_name] = item
        
        logger.info(
            f"Created unified dataset with {len(unified['time_series'])} time points"
        )
        
        return unified
    
    def validate_compatibility(
        self,
        source_model: str,
        target_model: str,
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate if source data is compatible with target model.
        
        Args:
            source_model: Source model name
            target_model: Target model name
            source_data: Source data to validate
            
        Returns:
            Validation report with missing/invalid fields
        """
        key = f"{source_model}->{target_model}"
        mapping = self.mappings.get(key)
        
        if not mapping:
            return {
                "compatible": True,
                "message": "No mapping defined, assuming compatibility"
            }
        
        required_fields = set(mapping.field_mappings.values())
        available_fields = set(source_data.keys())
        missing_fields = required_fields - available_fields
        
        validation = {
            "compatible": len(missing_fields) == 0,
            "missing_fields": list(missing_fields),
            "available_fields": list(available_fields),
            "can_use_defaults": all(
                field in mapping.defaults 
                for field in missing_fields
            )
        }
        
        return validation
