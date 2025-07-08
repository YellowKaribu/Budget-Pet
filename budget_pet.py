#!/usr/bin/env python3
from datetime import datetime;
import json
import os
from decimal import Decimal, InvalidOperation
from typing import Callable, Literal, TypedDict
import sys #for sys.exit()
from functools import wraps
from typing import TextIO
from dataclasses import dataclass
from enum import Enum

# === Constants and Configuration ===
TRANSACTION_LOG_FILE = "data/budget_log.txt"
BUDGET_STATE_FILE = "data/budget_state.json"
EXPENSE_CATEGORY = {
    "1": "Еда",
    "2": "Коммуналка",
    "3": "Лекарства",
    "4": "Развлечения",
    "5": "Прочее"
    }

MESSAGE_SEPARATOR = "----------------------"

# === Data Structures ===
@dataclass
class LogEntry:
    operation_type: str
    operation_id: int
    operation_date: str
    operation_amount: str
    category: str
    comment: str

@dataclass
class TransactionType (Enum):
    INCOME_WITH_TAX = "income_with_tax"
    INCOME_NO_TAX = "income_no_tax"
    EXPENSE = "expense"

@dataclass
class TaxRate (Enum):
    TAX = "0.2"
    RESERVE = "0.8"


class UserCancelledError(Exception):
    """Raised when the user cancels the current operation."""
    pass


USER_MESSAGES = {
    "info_operation_logged": "Операция успешно записана.",
    "info_exit_message": "Программа завершена. До свидания!",
    "info_operation_cancelled": "Операция отменена. Возврат в меню.",
    "error_input_invalid": "Неверный ввод данных.",
    "error_zero_amount": "Сумма не может быть нулевой.",
    "prompt_individual_entrepreneurship": "Доход от ИП? Да/нет: ",
    "prompt_operation_type":"Введите + для дохода, - для расхода: ",
    "prompt_transaction_amount": "Введите сумму транзакции: ",
    "prompt_comment": "Введите комментарий к операции: ",
    "prompt_expense_category": 
        "Выберите категорию расхода. 1-еда, 2-коммуналка, " \
        "3-лекарства, 4-развлечения, 5-прочее " \
        "или нажмите cancel для отмены операции: ",
    "prompt_start_menu_text": 
        "Добро пожаловать в финансовый трекер личных расходов.\n"
        "В любой момент введите cancel, чтобы вернуться в это меню.\n\n"
        "Введите: add (добавить расход/доход), balance "\
        "(ВРЕМЕННО НЕ РАБОТАЕТ), exit (выйти): "
    
}


# === Utility Functions (Helpers) ==
def get_current_date() -> str:
    '''Get today date.'''
    return datetime.now().date().strftime('%d-%m-%Y')


def get_last_operation_id() -> int:
    """
    Determine the next operation ID based on the number of data rows
    in the transaction log. Assumes first two lines are header.
    """
    try:
        with open(TRANSACTION_LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            data_lines = lines[2:] if len(lines) >= 2 else []
            return len(data_lines) + 1  # ID starts from 1
    except FileNotFoundError:
        return 1


def get_valid_category_prompt() -> str:
    """Ask the user until he provides a valid category key."""
    while True:
        key = user_input(USER_MESSAGES["prompt_expense_category"])
        category = EXPENSE_CATEGORY.get(key)
        if category:
            return category
        notify(USER_MESSAGES["error_input_invalid"])


def ask_transaction_comment() -> str:
    '''Ask user for transaction comment'''
    return user_input(USER_MESSAGES["prompt_comment"])


def ask_transaction_amount() -> str:
    """Prompt user for a transaction amount and validate it."""
    while True:
        user_amount = user_input(USER_MESSAGES["prompt_transaction_amount"])
        try:
            amount = Decimal(user_amount)
            if amount <= 0:
                notify(USER_MESSAGES["error_zero_amount"])
                continue
            return str(amount)
        except InvalidOperation:
            notify(USER_MESSAGES["error_input_invalid"])


def ask_transaction_category(type: TransactionType) -> str:
    """Prompt the user to select an expense category by number."""
    return get_valid_category_prompt() if type == TransactionType.EXPENSE else ""
    

def choose_tax_status() -> TransactionType:
    """Prompt the user if income is from individual entrepreneurship(taxed)."""
    while True:
        tax_status = user_input(USER_MESSAGES["prompt_individual_entrepreneurship"])
        match tax_status:
            case "да": 
                return TransactionType.INCOME_WITH_TAX
            case "нет": 
                return TransactionType.INCOME_NO_TAX
            case _: notify(USER_MESSAGES["error_input_invalid"])
            

def ask_transaction_type() -> TransactionType:
    """
    Prompt the user to choose a transaction type:
    '+' for income (with or without tax, clarified via a follow-up question),
    '-' for expense.
    """

    while True:
        user_input_type = user_input(USER_MESSAGES["prompt_operation_type"])
        if user_input_type == "+":
            return choose_tax_status()
        elif user_input_type == "-":
            return TransactionType.EXPENSE
        else:
            notify(USER_MESSAGES["error_input_invalid"])
    

# === Notification and Input/Output ===
def notify(message: str) -> None:
    """Print text from MESSAGES dictionary."""
    print(MESSAGE_SEPARATOR)
    print(message)


def wait_for_user_command():
    while True:
        user_choice = user_input(USER_MESSAGES["prompt_start_menu_text"])
        if user_choice in MENU_OPTIONS:
            return user_choice
        else:
            notify(USER_MESSAGES["error_input_invalid"])


def user_input(prompt: str) -> str:
    value = input(prompt).strip().lower()
    if value in ("cancel", "menu", "отмена"):
        raise UserCancelledError("User cancelled the operation.")
    return value


# === Decorators for File Handling ===
def open_budget_file_r(func):
    """Open the budget file in read mode and pass the file handle."""
    def wrapper(*args, **kwargs):
        with open(BUDGET_STATE_FILE, "r", encoding="utf-8") as f:
            return func(f, *args, **kwargs)
    return wrapper


def open_budget_file_w(func):
    """Open the budget file in write mode."""
    def wrapper(*args, **kwargs):
        with open(BUDGET_STATE_FILE, "w", encoding="utf-8") as f:
            return func(f, *args, **kwargs)
    return wrapper


def open_log_file_a(func):
    """Open the log file in append mode."""
    def wrapper(log_entry):
        with open(TRANSACTION_LOG_FILE, "a",  encoding="utf-8") as f:
            return func(log_entry, f)
    return wrapper


# === Budget State Management ===
@open_budget_file_r
def get_current_available_state(budget_file: TextIO) -> dict:
    """Load available budget state from JSON file."""
    try:
        return json.load(budget_file)
    except FileNotFoundError:
        return {"available_funds": "0", "reserve": "0", "taxes": "0"}


# === Logging ===
@open_log_file_a
def log_transaction(transaction_details: LogEntry, file_handle: TextIO) -> None:
    """Log a transaction to the file."""
    file_handle.write(f"|{transaction_details.operation_id:^5}|"
            f"{transaction_details.operation_date:^15}|"
            f"{transaction_details.operation_type:^18}|"
            f"{transaction_details.operation_amount:^11}|"
            f"{transaction_details.category:^19}| "
            f"{transaction_details.comment}\n")
    

# === Domain Logic (Business Logic) ===
def exit_application() -> None:
    '''Exit the application with a farewell message.'''

    notify(USER_MESSAGES["info_exit_message"])
    sys.exit()


@open_budget_file_w
def save_updated_state_to_file(file_handle: TextIO, updated_state: dict) -> None:
    """Save updated balance to the JSON state file."""
    json.dump(updated_state, file_handle, indent=4)


def apply_income_with_tax(budget_state: dict, transaction_details: LogEntry) -> dict:
    """Apply taxed income to budget state: 80% to reserve, 20% to taxes."""

    # Convert string values to Decimals for accurate calculations
    decimal_transaction_amount = Decimal(transaction_details.operation_amount)
    decimal_tax_modifier = Decimal(TaxRate.TAX.value)
    decimal_reserve_modifier = Decimal(TaxRate.RESERVE.value)
    decimal_reserve_state = Decimal(budget_state["reserve"])
    decimal_taxes_state = Decimal(budget_state["taxes"])

    # Distribute the amount between reserve and taxes
    budget_state["reserve"] = str(decimal_reserve_state + decimal_transaction_amount * decimal_reserve_modifier)
    budget_state["taxes"] = str(decimal_taxes_state + decimal_transaction_amount * decimal_tax_modifier)

    return budget_state


def apply_income_no_tax(budget_state: dict, transaction_details: LogEntry) -> dict:
    """Apply income to budget state: 100% to reserve."""

    # Convert string values to Decimals for accurate calculations
    decimal_transaction_amount = Decimal(transaction_details.operation_amount)
    decimal_reserve_state = Decimal(budget_state["reserve"])

    # Distribute the amount between reserve and taxes
    budget_state["reserve"] = str(decimal_reserve_state + decimal_transaction_amount)

    return budget_state


def apply_expense(budget_state: dict, transaction_details: LogEntry) -> dict:
    """Apply expense to budget by subtracting from available funds."""
    decimal_amount = Decimal(transaction_details.operation_amount)
    decimal_available_funds = Decimal(budget_state["available_funds"])
    budget_state["available_funds"] = str(decimal_available_funds - decimal_amount)
    return budget_state


def collect_transaction_details() -> LogEntry:
    """Collect transaction data from user input and other functions."""

    transaction_id = get_last_operation_id()
    date = get_current_date()
    transaction_type = ask_transaction_type()
    amount = ask_transaction_amount()
    category = ask_transaction_category(transaction_type)
    comment = ask_transaction_comment()
    return LogEntry(
        transaction_type.value,
        transaction_id, 
        date, 
        amount, 
        category, 
        comment, 
    )


def process_transaction_type(current_state: dict, transaction: LogEntry) -> dict:
    """Route transaction to appropriate handler based on type and tax status."""

    if transaction.operation_type == TransactionType.EXPENSE.value:
        return apply_expense(current_state, transaction)
    elif transaction.operation_type == TransactionType.INCOME_WITH_TAX.value:
        return apply_income_with_tax(current_state, transaction)
    elif transaction.operation_type == TransactionType.INCOME_NO_TAX.value:
        return apply_income_no_tax(current_state, transaction)
    else:
        raise ValueError(f"Unsupported transaction type: {transaction.operation_type}")


def process_transaction(transaction_details: LogEntry) -> None:
    current_state = get_current_available_state()
    updated_state = process_transaction_type(current_state, transaction_details)
    save_updated_state_to_file(updated_state)


# — High‑level functions
def run_transaction() -> None:
    try:
        details = collect_transaction_details()
        process_transaction(details)
        log_transaction(details)
        notify(USER_MESSAGES["info_operation_logged"]) 
    except UserCancelledError:
        notify(USER_MESSAGES["info_operation_cancelled"])


def handle_balance_operations():
    """Run the secondary main loop for working with the budget state."""    
    pass


MENU_OPTIONS = {
    "add": run_transaction,
    "balance": handle_balance_operations,
    "exit": exit_application
}


def main() -> None:
    '''Run the main application loop and route user actions.'''

    while True:
        user_choice = wait_for_user_command()
        action = MENU_OPTIONS[user_choice]
        action()


if __name__ == "__main__":
    main()