from budgetpet.domain.interfaces import IBudgetRepository, ILogger
from budgetpet.domain.models import BudgetState
from decimal import Decimal, InvalidOperation


class BudgetService:
    def __init__(self, repository: IBudgetRepository, logger: ILogger) -> None:
        self.repository = repository
        self.logger = logger
        

    def save_budget_state(self, data: dict) -> None:
        required_fields = ['reserve', 'available_funds', 'rent', 'taxes']
        if not data or any(field not in data for field in required_fields):
            self.logger.error("Missing required fields in budget state data")
            raise ValueError("Missing required fields")
        
        try:
            state = BudgetState(
                reserve=Decimal(str(data['reserve'])),
                available_funds=Decimal(str(data['available_funds'])),
                rent=Decimal(str(data['rent'])),
                taxes=Decimal(str(data['taxes']))
            )
            self.repository.save_budget_state(state, cursor=None)
        except (InvalidOperation, ValueError, TypeError) as e:
            self.logger.error(f"Invalid budget state data: {e}")
            raise ValueError("Invalid data format")

    def get_budget_state(self) -> BudgetState:
        try:
            return self.repository.get_current_budget_state(cursor=None)
        except Exception as e:
            self.logger.error(f"Error fetching budget state: {e}")
            raise

