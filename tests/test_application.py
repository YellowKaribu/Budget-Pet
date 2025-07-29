from budgetpet.logger import logger
from unittest.mock import patch, MagicMock
from budgetpet.application import should_run_monthly_event, pay_rent
from budgetpet.models import BudgetState
from decimal import Decimal
from datetime import date


def test_should_run_monthly_event_runs_events() -> None:
    '''Check if monthly events runs at all'''
    fake_events = [
        {"id": 1, "trigger_day": 29, "last_executed": None},
        {"id": 2, "trigger_day": 1, "last_executed": None}
    ]

    #what events we want to run
    fake_events_to_run = [1, 2]

    with patch("budgetpet.application.get_monthly_events", return_value=fake_events) as mock_get_events, \
        patch("budgetpet.application.check_day_of_monthly_events", return_value=fake_events_to_run) as mock_check_day_of_monthly_events, \
        patch("budgetpet.application.run_monthly_event") as mock_run_events:

        should_run_monthly_event()

        mock_get_events.assert_called_once()
        mock_check_day_of_monthly_events.assert_called_once_with(fake_events)
        mock_run_events.assert_called_once_with(fake_events_to_run)


def test_should_run_monthly_event_no_events_to_run():
    '''Check if no events run, if they should not'''
    with patch("budgetpet.application.get_monthly_events", return_value=[]) as mock_get_events, \
         patch("budgetpet.application.check_day_of_monthly_events", return_value=[]) as mock_check_events, \
         patch("budgetpet.application.run_monthly_event") as mock_run_events:

        should_run_monthly_event()

        mock_get_events.assert_called_once()
        mock_check_events.assert_called_once_with([])
        mock_run_events.assert_not_called()


def test_pay_rent() -> None:
    '''Test that rent pay really become 0'''

    fake_balance = BudgetState(
        reserve=Decimal("1000"),
        available_funds=Decimal("1000"),
        rent=Decimal("810"),
        taxes=Decimal("1000")
    )
    fake_id = 1
    fake_today = date(2025, 7, 1)

    mock_cursor = MagicMock()
    with patch("budgetpet.application.db_cursor") as mock_db_cursor, \
        patch("budgetpet.application.get_current_budget_state", return_value=fake_balance) as mock_get_current_budget_state, \
        patch("budgetpet.application.save_budget_state") as mock_save_budget_state, \
        patch("budgetpet.application.date") as mock_date, \
        patch("budgetpet.application.update_monthly_event") as mock_update_monthly_event:

        mock_cm = MagicMock() #context manager
        mock_cm.__enter__.return_value = mock_cursor
        mock_db_cursor.return_value = mock_cm #mock db_cursor call

        mock_date.today.return_value = fake_today
        
        pay_rent(fake_id)

        mock_get_current_budget_state.assert_called_once_with(mock_cursor)
        updated_arg = mock_save_budget_state.call_args[0][0]
        assert updated_arg != fake_balance 
        assert updated_arg.rent == Decimal("0")

        mock_save_budget_state.assert_called_once_with(updated_arg, mock_cursor)
        mock_update_monthly_event.assert_called_once_with(fake_id, fake_today)