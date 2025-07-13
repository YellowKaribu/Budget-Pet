from unittest.mock import patch
from adapters.cli_input_adapter import CLIInputAdapter
from config.messages import (
    get_err_empty_input,
    get_err_input_not_a_number,
    get_err_zero_amount,
    get_err_invalid_input
    )
import pytest
import builtins
from core.exceptions import CancelledTransaction
from main import main

def test_prompt_transaction_type_income():
    adapter = CLIInputAdapter()

    with patch("builtins.input", return_value="+"):
        result = adapter.prompt_transaction_type()
        assert result == "income"


def test_prompt_transaction_type_expense():
    adapter = CLIInputAdapter()

    with patch("builtins.input", return_value="-"):
        result = adapter.prompt_transaction_type()
        assert result == "expense"


def test_prompt_transaction_amount_empty_input():
    # Ensure that empty input is rejected and error message is printed
    # Then check that valid input '1.2' or '1,2' is accepted
    adapter = CLIInputAdapter()

    with patch("builtins.input", side_effect=["", "1.2", "1,2"]), \
        patch("builtins.print") as mock_print:
        adapter.prompt_transaction_amount()
        mock_print.assert_any_call(get_err_empty_input())


def test_prompt_transaction_amount_numbers():
    # Ensure that not-number is rejected and error message is printed
    # Then check that valid input '123' is accepted
    adapter = CLIInputAdapter()

    with patch("builtins.input", side_effect=["abc","123"]), \
        patch("builtins.print") as mock_print:
        adapter.prompt_transaction_amount()
        mock_print.assert_any_call(get_err_input_not_a_number())


def test_prompt_transaction_amount_zero():
    # Ensure that '0' is rejected and error message is printed
    # Then check that valid input '123' is accepted
    adapter = CLIInputAdapter()

    with patch("builtins.input", side_effect=["0", "123"]), \
        patch("builtins.print") as mock_print:

        adapter.prompt_transaction_amount()
        mock_print.assert_any_call(get_err_zero_amount())


def test_prompt_transaction_category():
    adapter = CLIInputAdapter()

    with patch("builtins.input", side_effect=["abc", "1"]), \
        patch("builtins.print") as mock_print:

        adapter.prompt_transaction_category()
        mock_print.assert_any_call(get_err_invalid_input())


def test_prompt_tax_status():
    adapter = CLIInputAdapter()
    
    with patch("builtins.input", side_effect=["abc", "да"]), \
        patch("builtins.print") as mock_print:

        adapter.prompt_tax_status()
        mock_print.assert_any_call(get_err_invalid_input())


@pytest.mark.parametrize("method_name", [
    "prompt_transaction_type",
    "prompt_transaction_amount",
    "prompt_transaction_category",
    "prompt_transaction_comment",
    "prompt_tax_status",
])
def test_all_prompt_methods_raise_cancel_prompt(monkeypatch, method_name):
    adapter = CLIInputAdapter()

    monkeypatch.setattr("builtins.input", lambda _: "отмена")

    method = getattr(adapter, method_name)

    with pytest.raises(CancelledTransaction):
        method()
