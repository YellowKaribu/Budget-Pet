from abc import ABC, abstractmethod
from budgetpet.domain.models import BudgetState, Operation, StatisticFilters
from typing import List, Any, Dict
from datetime import date
from typing import Optional, Any

class IBudgetRepository(ABC):
#Optional cursor allows open 1 database connection for multiple functions in service
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
    def get_operation_by_id(self, operation_data: Operation, cursor: Optional[Any] = None) -> Operation:
        pass

    @abstractmethod
    def add_operation_history(self, operation_data: dict, cursor: Optional[Any] = None) -> None:
        pass

    @abstractmethod
    def delete_operation(self, operation_data: Operation, cursor) -> None:
        pass

    @abstractmethod
    def update_operation(self, new_data: dict, cursor) -> None:
        pass

    @abstractmethod
    def get_statistic_from_db(self, user_filters: StatisticFilters) -> List[Any]:
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

        pass 