"""Coupling engine for model chaining"""
from datetime import datetime

class BaseModel:
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}
        self.output = None
        self.metadata = {"run_time": None, "status": "initialized"}
    def validate_input(self, data): return True
    def run(self, input_data): raise NotImplementedError
    def get_output(self):
        return {"model": self.name,
            "output": self.output,
            "metadata": {**self.metadata,
            "timestamp": datetime.now().isoformat()}}
class ModelChain:
    def __init__(self): self.models, self.data_flow = {}, []
    def add_model(self, name, model): self.models[name] = model; return self
    def connect(self, from_model, to_model, mapping):
        self.data_flow.append({"from": from_model, "to": to_model, "mapping": mapping}); return self
    def run_chain(self, initial_input):
        current_data = initial_input.copy(); results = {}
        for name, model in self.models.items():
            if not model.validate_input(current_data): continue
            output = model.run(current_data); results[name] = output
            for conn in self.data_flow:
                if conn["from"] == name:
                    for out_k, in_k in conn["mapping"].items():
                        if out_k in output.get("output", {}): current_data[in_k] = output["output"][out_k]
        return {"chain_complete": True,
            "results": results,
            "final_output": current_data,
            "timestamp": datetime.now().isoformat()}