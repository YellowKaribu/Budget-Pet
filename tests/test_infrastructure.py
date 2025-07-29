from budgetpet.infrastructure import get_monthly_events
from budgetpet.constants import EXPENSE_CATEGORY

def test_print_last_executed_day():
    result = get_monthly_events()
    print(result)
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)

