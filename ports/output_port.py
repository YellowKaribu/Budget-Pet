from core.entities import BudgetState
from config.config import BUDGET_STATE
from typing import Protocol

class BudgetStatePort(Protocol):
    def get_state(self) -> BudgetState:
        ...

    def save_state(self, updated_state) -> None:
        pass


class NotifierPort(Protocol):
    def notify_success(self, message: str) -> None:
        ...
        
    def show_log_record(self, logs: list[dict], expense_category) -> None:
        ...

    def show_budget_state(self, budget_state: BudgetState) -> None:
        ...


class TransactionsLogPort(Protocol):

    def get_transaction_log(self) -> list[dict]:
        ...

    def write_transaction_log(self, entry: dict) -> None:
        ...