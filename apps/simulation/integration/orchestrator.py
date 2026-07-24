"""
Simulation Orchestrator for Eco Nozhin
=======================================
Coordinates multi-model simulations and manages workflows.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported simulation models."""
    ROTH_C = "rothc"
    SWAT = "swat"
    APSIM = "apsim"
    DSSAT = "dssat"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class SimulationWorkflow:
    """Definition of a multi-model simulation workflow."""
    
    workflow_id: str
    name: str
    description: str = ""
    
    # Models to run in order
    models: List[ModelType] = field(default_factory=list)
    
    # Dependencies between models
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    # Shared parameters
    shared_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Execution options
    parallel_execution: bool = False
    stop_on_failure: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    status: WorkflowStatus = WorkflowStatus.PENDING
    
    def add_model(self, model: ModelType, dependencies: Optional[List[str]] = None):
        """Add a model to the workflow."""
        self.models.append(model)
        if dependencies:
            self.dependencies[model.value] = dependencies
    
    def validate(self) -> bool:
        """Validate workflow configuration."""
        if not self.models:
            raise ValueError("Workflow must have at least one model")
        
        # Check for circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(model: str) -> bool:
            visited.add(model)
            rec_stack.add(model)
            
            for dep in self.dependencies.get(model, []):
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(model)
            return False
        
        for model in self.models:
            if model.value not in visited:
                if has_cycle(model.value):
                    raise ValueError("Circular dependency detected in workflow")
        
        return True


@dataclass
class WorkflowResult:
    """Results from workflow execution."""
    
    workflow_id: str
    status: WorkflowStatus
    start_time: datetime
    end_time: datetime
    execution_time_seconds: float
    
    # Individual model results
    model_results: Dict[str, Any] = field(default_factory=dict)
    
    # Errors
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "execution_time_seconds": self.execution_time_seconds,
            "model_results": self.model_results,
            "errors": self.errors,
            "warnings": self.warnings
        }


class SimulationOrchestrator:
    """
    Main orchestrator for multi-model simulations.
    
    Coordinates execution of RothC, SWAT, APSIM, and DSSAT models,
    handling data flow between models and aggregating results.
    """
    
    def __init__(self, working_directory: Optional[Path] = None):
        """
        Initialize orchestrator.
        
        Args:
            working_directory: Base directory for simulation outputs
        """
        self.working_directory = working_directory or Path("./simulations")
        self.working_directory.mkdir(parents=True, exist_ok=True)
        
        # Model instances (lazy-loaded)
        self._model_instances: Dict[ModelType, Any] = {}
        
        logger.info(f"SimulationOrchestrator initialized: {self.working_directory}")
    
    def _get_model_instance(self, model_type: ModelType):
        """Get or create model instance."""
        if model_type not in self._model_instances:
            if model_type == ModelType.ROTH_C:
                from apps.simulation.carbon_cycle.rothc import RothCWrapper
                self._model_instances[model_type] = RothCWrapper(
                    self.working_directory / "rothc"
                )
            elif model_type == ModelType.SWAT:
                from apps.simulation.hydrology.swat import SWATWrapper
                self._model_instances[model_type] = SWATWrapper(
                    working_directory=self.working_directory / "swat"
                )
            elif model_type == ModelType.APSIM:
                from apps.simulation.agriculture.apsim import APSIMWrapper
                self._model_instances[model_type] = APSIMWrapper(
                    working_directory=self.working_directory / "apsim"
                )
            elif model_type == ModelType.DSSAT:
                from apps.simulation.agriculture.dssat import DSSATWrapper
                self._model_instances[model_type] = DSSATWrapper(
                    working_directory=self.working_directory / "dssat"
                )
        
        return self._model_instances[model_type]
    
    def create_workflow(
        self,
        name: str,
        models: List[ModelType],
        description: str = "",
        **kwargs
    ) -> SimulationWorkflow:
        """
        Create a new simulation workflow.
        
        Args:
            name: Workflow name
            models: List of models to include
            description: Workflow description
            **kwargs: Additional workflow parameters
            
        Returns:
            Configured SimulationWorkflow
        """
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow = SimulationWorkflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            models=models,
            **kwargs
        )
        
        workflow.validate()
        logger.info(f"Created workflow: {workflow_id} ({name})")
        
        return workflow
    
    def execute_workflow(
        self,
        workflow: SimulationWorkflow,
        input_data: Dict[str, Any]
    ) -> WorkflowResult:
        """
        Execute a simulation workflow.
        
        Args:
            workflow: Workflow to execute
            input_data: Input parameters for models
            
        Returns:
            WorkflowResult with all model outputs
        """
        logger.info(f"Executing workflow: {workflow.workflow_id}")
        
        start_time = datetime.now()
        model_results = {}
        errors = []
        warnings = []
        
        try:
            for model_type in workflow.models:
                # Check dependencies
                deps = workflow.dependencies.get(model_type.value, [])
                for dep in deps:
                    if dep not in model_results:
                        raise RuntimeError(
                            f"Dependency {dep} not satisfied for {model_type.value}"
                        )
                
                # Get model instance
                model = self._get_model_instance(model_type)
                
                # Prepare input for this model
                model_input = self._prepare_model_input(
                    model_type,
                    input_data,
                    model_results
                )
                
                try:
                    # Run model
                    logger.info(f"Running {model_type.value}...")
                    result = model.run(model_input)
                    model_results[model_type.value] = result
                    logger.info(f"{model_type.value} completed successfully")
                    
                except Exception as e:
                    error_msg = f"{model_type.value} failed: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    
                    if workflow.stop_on_failure:
                        raise
                
            status = WorkflowStatus.COMPLETED if not errors else WorkflowStatus.PARTIAL
            
        except Exception as e:
            status = WorkflowStatus.FAILED
            errors.append(str(e))
            logger.error(f"Workflow failed: {e}")
        
        end_time = datetime.now()
        
        result = WorkflowResult(
            workflow_id=workflow.workflow_id,
            status=status,
            start_time=start_time,
            end_time=end_time,
            execution_time_seconds=(end_time - start_time).total_seconds(),
            model_results=model_results,
            errors=errors,
            warnings=warnings
        )
        
        logger.info(
            f"Workflow {workflow.workflow_id} completed: {status.value} "
            f"in {result.execution_time_seconds:.2f}s"
        )
        
        return result
    
    def _prepare_model_input(
        self,
        model_type: ModelType,
        input_data: Dict[str, Any],
        previous_results: Dict[str, Any]
    ):
        """
        Prepare input for a specific model.
        
        Uses shared parameters and outputs from previous models.
        """
        # This is a simplified implementation
        # A full implementation would map outputs from previous models
        # to inputs for the current model
        
        if model_type == ModelType.ROTH_C:
            from apps.simulation.carbon_cycle.rothc.wrapper import RothCInput
            return RothCInput(**input_data.get('rothc', {}))
        
        elif model_type == ModelType.SWAT:
            from apps.simulation.hydrology.swat.wrapper import SWATInput
            return SWATInput(**input_data.get('swat', {}))
        
        elif model_type == ModelType.APSIM:
            from apps.simulation.agriculture.apsim.wrapper import APSIMInput
            return APSIMInput(**input_data.get('apsim', {}))
        
        elif model_type == ModelType.DSSAT:
            from apps.simulation.agriculture.dssat.wrapper import DSSATInput
            return DSSATInput(**input_data.get('dssat', {}))
        
        return input_data
    
    def run_parallel(
        self,
        workflows: List[SimulationWorkflow],
        input_datasets: List[Dict[str, Any]]
    ) -> List[WorkflowResult]:
        """
        Run multiple workflows in parallel.
        
        Args:
            workflows: List of workflows to run
            input_datasets: Corresponding input datasets
            
        Returns:
            List of WorkflowResults
        """
        import asyncio
        
        async def run_async(workflow, inputs):
            return self.execute_workflow(workflow, inputs)
        
        tasks = [
            run_async(wf, inputs) 
            for wf, inputs in zip(workflows, input_datasets)
        ]
        
        loop = asyncio.new_event_loop()
        results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        
        return results
