
from decimal import Decimal
from unittest.mock import MagicMock, patch
from budgetpet.domain.models import BudgetState
from budgetpet.infrastructure.persistence.mysql_repository import MySQLBudgetRepository

@patch('budgetpet.infrastructure.persistence.mysql_repository.get_db_cursor')
def test_save_budget_state(mock_get_cursor):
    mock_cursor = MagicMock()
    mock_get_cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.rowcount = 1

    repo = MySQLBudgetRepository()
    state = BudgetState(
        reserve=Decimal('100.0'),
        available_funds=Decimal('200.0'),
        rent=Decimal('300.0'),
        taxes=Decimal('400.0')
    )

    repo.save_budget_state(state)

    mock_cursor.execute.assert_called_once()


