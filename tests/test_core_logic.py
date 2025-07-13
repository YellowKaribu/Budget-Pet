import pytest
from decimal import Decimal, InvalidOperation
from core.entities import TransactionInputData, ParsedTransaction, BudgetState
from core.use_cases import (
    parse_transaction_input,
    apply_transaction_to_state,
    build_log_entry,
    pay_rent
    )

from datetime import datetime, date
from adapters.transaction_log_jsonl_adapter import TransactionsLoggerJsonl

def test_parse_valid_income():
    input_data = TransactionInputData(
        type="Income",
        amount="1000.50",
        comment="Зарплата",
        category=None,
        tax_status="нет"
    )
    parsed = parse_transaction_input(input_data)
    assert parsed.type == "income_no_tax"
    assert parsed.amount == Decimal("1000.50")

def test_parse_valid_expense_with_whitespace():
    input_data = TransactionInputData(
        type="  Expense ",
        amount=" 200 ",
        comment="Еда",
        category=None,
        tax_status="нет"
    )
    parsed = parse_transaction_input(input_data)
    assert parsed.type == "expense"
    assert parsed.amount == Decimal("200")

def test_parse_invalid_amount_raises():
    input_data = TransactionInputData(
        type="income",
        amount="not_a_number",
        comment="Ошибка",
        category=None,
        tax_status=None
    )
    with pytest.raises(InvalidOperation):
        parse_transaction_input(input_data)


def make_initial_state() -> BudgetState:
    return BudgetState(
        reserve="1000",
        available_funds="500",
        rent="0",
        taxes="0"
    )

def test_income_no_tax():
    state = make_initial_state()
    tx = ParsedTransaction(type="income_no_tax", amount=Decimal("200"))
    new_state = apply_transaction_to_state(tx, state)
    assert new_state.reserve == "1200"
    assert new_state.available_funds == "500"
    assert new_state.taxes == "0"

def test_income_with_tax():
    state = make_initial_state()
    tx = ParsedTransaction(type="income_with_tax", amount=Decimal("100"))
    new_state = apply_transaction_to_state(tx, state)
    assert new_state.reserve == "1080.0"      # 1000 + 80
    assert new_state.taxes == "20.0"          # 0 + 20

def test_expense():
    state = make_initial_state()
    tx = ParsedTransaction(type="expense", amount=Decimal("150"))
    new_state = apply_transaction_to_state(tx, state)
    assert new_state.available_funds == "350"  # 500 - 150
    assert new_state.reserve == "1000"

def test_invalid_type_raises():
    state = make_initial_state()
    tx = ParsedTransaction(type="donation", amount=Decimal("50"))
    with pytest.raises(ValueError):
        apply_transaction_to_state(tx, state)


def test_build_entry_log():
    data = TransactionInputData(
        "income",
        "100", 
        "testcomment", 
        "1",
        "нет"
    )
    port = TransactionsLoggerJsonl()
    new_data = build_log_entry(data, port)
    first_key = next(iter(new_data))
    first_value = new_data[first_key]
    assert type(new_data) == dict
    assert "id" in new_data
    assert "timestamp" in new_data

    try:
        parsed = datetime.strptime(new_data["timestamp"], "%d-%m-%Y %H:%M:%S")

    except ValueError:
        pytest.fail("timestamp has incorrect format")


class DummyBudgetStatePort():
    def __init__(self, budget_state: BudgetState) -> None:
        self.state = budget_state
        self.saved_state = None

    def get_state(self) -> BudgetState:
        return self.state

    def save_state(self, updated_state) -> None:
        self.saved_state = updated_state
  

class DummyMetaFilePort():
    def __init__(self, data: dict) -> None:
        self.meta_data = data
        self.saved_data = None

    def get_meta_data(self, meta_file) -> dict:
        return self.meta_data
    
    def save_meta_data(self, meta_file, meta_data: dict) -> None:
        self.saved_data = meta_data


def test_pay_rent() -> None:
    """Tests the pay_rent function:
    - Ensures the 'rent' field is reset to "0" while other budget fields remain unchanged.
    - Updates the 'last_rent_pay' field in metadata to today's date.
    - Confirms both budget state and metadata are correctly saved.
    """
    budget_state = BudgetState(
        reserve="1000",
        available_funds="1000",
        rent="1000",
        taxes="1000"
    )

    meta_state = {
    "last_rent_pay": "",
    "last_report_month": ""
    }

    budget_port = DummyBudgetStatePort(budget_state)
    meta_port = DummyMetaFilePort(meta_state)

    pay_rent(budget_port, meta_port)

    assert budget_port.saved_state is not None
    assert budget_port.saved_state.reserve == "1000"
    assert budget_port.saved_state.available_funds == "1000"
    assert budget_port.saved_state.rent == "0"
    assert budget_port.saved_state.taxes == "1000"
    assert meta_port.saved_data is not None
    assert "last_rent_pay" in meta_port.saved_data
    saved_date = datetime.strptime(meta_port.saved_data["last_rent_pay"], "%Y-%m-%d").date()
    assert saved_date == date.today()


