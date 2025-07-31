from decimal import Decimal
from unittest.mock import MagicMock
import pytest
from budgetpet.application.services.budget_service import BudgetService
from budgetpet.application.services.operation_service import OperationService
from budgetpet.domain.models import BudgetState, DBError


#BudgetService
def test_update_budget_state_success():
    mock_rep = MagicMock()
    mock_logger = MagicMock()

    service = BudgetService(mock_rep, mock_logger)

    data = {
        'reserve': '100',
        'available_funds': '200',
        'rent': '300',
        'taxes': '400'
    }

    service.save_budget_state(data)

    expected_state = BudgetState(
        reserve=Decimal('100.0'),
        available_funds=Decimal('200.0'),
        rent=Decimal('300.0'),
        taxes=Decimal('400.0')
    )

    mock_rep.save_budget_state.assert_called_once_with(expected_state)
    mock_logger.error.assert_not_called


def test_update_budget_state_missing_data_fields():
    mock_rep = MagicMock()
    mock_logger = MagicMock()
    service = BudgetService(mock_rep, mock_logger)

    with pytest.raises(ValueError):
        service.save_budget_state({'reserve': '100'})

    mock_logger.error.assert_called_once()
    mock_rep.save_budget_state.assert_not_called()


def test_update_budget_state_invalid_format():
    mock_repo = MagicMock()
    mock_logger = MagicMock()
    service = BudgetService(mock_repo, mock_logger)

    data = {
        'reserve': 'abc',
        'available_funds': '___',
        'rent': '100',
        'taxes': '200'
    }

    with pytest.raises(ValueError):
        service.save_budget_state(data)

    mock_repo.save_budget_state.assert_not_called()
    mock_logger.error.assert_called_once()


def test_get_budget_state_sucess():
    mock_rep = MagicMock()
    mock_logger = MagicMock()
    service = BudgetService(mock_rep, mock_logger)

    expected = BudgetState(
         reserve=Decimal('100.0'),
         available_funds=Decimal('200.0'),
         rent=Decimal('300.0'),
         taxes=Decimal('400.0')
    )

    mock_rep.get_current_budget_state.return_value = expected

    result = service.get_budget_state()
    assert result == expected
    mock_logger.error.assert_not_called()


def test_get_budget_state_repository_error():
    mock_rep = MagicMock()
    mock_logger = MagicMock()
    service = BudgetService(mock_rep, mock_logger)

    mock_rep.get_current_budget_state.side_effect = Exception('DB down')

    with pytest.raises(Exception):
        service.get_budget_state()

    mock_logger.error.assert_called_once()
    

#OperationService
def test_get_operations_history_success():
    mock_rep = MagicMock()
    mock_logger = MagicMock()
    service = OperationService(mock_rep, mock_logger)

    result = service.get_operations_history()

    mock_rep.get_operation_history.assert_called_once()


def test_get_operations_history_repository_error():
    mock_repo = MagicMock()
    mock_logger = MagicMock()
    service = OperationService(mock_repo, mock_logger)
    mock_repo.get_operation_history.side_effect = DBError()

    with pytest.raises(DBError):
        service.get_operations_history()

    mock_logger.error.assert_called_once()


def test_add_operation_success():
    mock_rep = MagicMock()
    mock_logger = MagicMock()

    data = {
        ''
    }

    service = OperationService(mock_rep, mock_logger, data: dict)



'''def add_operation(self, data: dict) -> None:
        try:
            self.repository.add_operation(data)
        except Exception as e:
            self.logger.error(f"Error adding operation: {e}")
            raise'''