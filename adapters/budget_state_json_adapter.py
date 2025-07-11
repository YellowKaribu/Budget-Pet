from core.entities import BudgetState
from ports.output_port import BudgetStatePort
from config.config import BUDGET_STATE
from typing import TextIO
import json
from dataclasses import asdict

class BudgetStateAdapter(BudgetStatePort):
    def get_state(self) -> BudgetState:
        with open(BUDGET_STATE, "r") as f:
            data = json.load(f)
            return BudgetState(**data)
    def save_state(self, state: BudgetState) -> None:
        with open(BUDGET_STATE, "w") as f:
            json.dump(asdict(state), f, indent=2)