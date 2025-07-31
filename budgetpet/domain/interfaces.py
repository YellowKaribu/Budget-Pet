from abc import ABC, abstractmethod
from budgetpet.domain.models import BudgetState
from typing import List, Any, Dict
from datetime import date
from typing import Optional, Any
import mysql.connector

class IBudgetRepository(ABC):
    @abstractmethod
    def save_budget_state(self, state: BudgetState, cursor: Optional[Any] = None) -> None:
        pass


    @abstractmethod
    def get_current_budget_state(self, cursor: Optional[Any] = None) -> BudgetState:
        pass

class IOperationsRepository(ABC):


    @abstractmethod
    def get_operation_history_from_db(self) -> List[Any]:
        pass


    @abstractmethod
    def add_operation(self, operation_data: dict, cursor: Optional[Any] = None) -> None:
        pass


    @abstractmethod
    def edit_operation(self, operation_id: int, operation_data: dict) -> None:
        pass


    @abstractmethod
    def delete_operation(self, operation_id: int) -> None:
        pass

class IEventsRepository(ABC):

    @abstractmethod
    def get_monthly_events(self) -> List[Dict]:
        pass


    @abstractmethod
    def update_monthly_event(self, event_id: int, last_executed: date) -> None:
        pass


class ILogger(ABC):
    @abstractmethod
    def debug(self, message: str) -> None:
        """Записывает отладочное сообщение."""
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        """Записывает сообщение об ошибке."""
        pass

    @abstractmethod
    def exception(self, message: str) -> None:
        """Записывает сообщение об исключении."""
        pass

    @abstractmethod
    def info(self, message: str) -> None:
        pass


class IOperationService(ABC):
    @abstractmethod
    def get_operations_history(self, cursor) -> list[dict]:
        pass


    @abstractmethod
    def add_operation(self, data: dict, cursor) -> None:
        pass


    @abstractmethod
    def edit_operation(self, operation_id: int, data: dict, cursor) -> None:
        pass


    @abstractmethod
    def delete_operation(self, operation_id: int, cursor) -> None:
        pass 