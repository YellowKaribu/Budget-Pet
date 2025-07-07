#!/usr/bin/env python3
from datetime import datetime;
import json
from decimal import Decimal, InvalidOperation
from typing import Callable, Literal
import sys #for sys.exit()
from functools import wraps
from typing import TextIO


TRANSACTION_LOG_FILE = "data/budget_log.txt"
BUDGET_STATE_FILE = "data/budget_state.json"
EXPENSE_CATEGORY = {
    "1": "Еда",
    "2": "Коммуналка",
    "3": "Лекарства",
    "4": "Развлечения",
    "5": "Прочее"
    }
USER_MESSAGES = {
    "info_operation_logged": "Операция успешно записана.",
    "error_input_invalid": "Неверный ввод данных.",
    "prompt_income_individual_entrepreneurship": "Доход от ИП? Да/нет: ",
    "prompt_operation_type":
        "Введите +сумма для дохода, -сумма для расхода, menu для выхода: ",
    "error_zero_amount": "Сумма не может быть нулевой.",
    "prompt_comment": "Введите комментарий к операции: ",
    "prompt_expense_category": 
        "Выберите категорию расхода. 1-еда, 2-коммуналка, " \
        "3-лекарства, 4-развлечения, 5-прочее: ",
    "info_exit_message": "Программа завершена. До свидания!",
    "prompt_start_menu_text": 
        "Выберите: add (добавить расход/доход), balance "\
        "(просмотреть состояние), exit (выйти)\nВаш выбор: "
}

MESSAGE_SEPARATOR = "----------------------"

# === File access decorators ===
def open_budget_file_r(func):
    """Open the budget file in read mode."""
    def wrapper():
        with open(BUDGET_STATE_FILE, "r") as f:
            return func(f)
    return wrapper


def open_budget_file_w(func):
    """Open the budget file in write mode."""
    def wrapper(*args, **kwargs):
        with open(BUDGET_STATE_FILE, "w") as f:
            return func(f, *args, **kwargs)
    return wrapper


# === Income/Expense Operations == #
def add_expense(expense_amount: str) -> None:
    """Subtract the expense amount from available funds state."""

    current_available_state = get_current_available_state()
    updated_state = subtract_expense(current_available_state, expense_amount)
    save_available_state(updated_state)


def subtract_expense(available_funds_state, expense_amount) -> dict:
    """Subtract expense amount from current available funds balance in state file.

    :return: dict - new available funds state after subtract operation.
    """
    available_funds_decimal = Decimal(available_funds_state["available_funds"])
    absolute_expense_decimal = abs(Decimal(expense_amount))
    available_funds_state["available_funds"] = str(available_funds_decimal - absolute_expense_decimal) 
    return available_funds_state


@open_budget_file_r
def get_current_available_state(state_file: TextIO) -> dict:
    """Load available funds state from JSON state file."""
    return json.load(state_file)


@open_budget_file_w
def save_available_state(state_file: TextIO, updated_state: dict) -> None:
    """Save updated available funds balance to the JSON state file."""
    json.dump(updated_state, state_file, indent=4)


# === Messages ang logging ===
def notify(message_key:
        Literal[
        "info_operation_logged",
        "error_input_invalid",
        "prompt_income_individual_entrepreneurship",
        "prompt_operation_type",
        "error_zero_amount",
        "prompt_comment",
        "prompt_expense_category",
        "info_exit_message",
        "prompt_start_menu_text"
        ]
    ) -> None:
    """Print text from MESSAGES dictionary."""

    message = USER_MESSAGES.get(message_key, f"Unknown message key: {message_key}")
    print(MESSAGE_SEPARATOR)
    print(message)

def log_financial_operation(raw_input: str, category: str, comment: str) -> None:
    """Append a formatted user operation to the log file and print 
    confirmation message."""

    today = get_current_date()
    operation_id = get_last_operation_id(TRANSACTION_LOG_FILE)

    write_log_record(TRANSACTION_LOG_FILE, 
                          operation_id, 
                          today, 
                          raw_input, 
                          category, 
                          comment)
    notify("info_operation_logged")

def write_log_record(
    log_file: str, 
    count: int, 
    operation_date: str, 
    transaction_amount: str, 
    category: str, 
    comment: str
) -> None:
    """Write a line in the log file with user input parameters.

    :param log_file: str - path to the log file.
    :param count: int - number of operacion.
    :param operation_date: str - today date which is counts with separate function.
    :param transaction_amount: str - user input representing an amount and what it is 
    - expence or earning (e.g. "-500").
    :param category: str - user input as number indicating the expense category 
    (e.g. "food").
    :param comment: str - optional user comment to describe the operation 
    (e.g. "lunch").
    :return: None - write a line to log file
    """
    
    with open(log_file, "a") as f:
        category_name = EXPENSE_CATEGORY.get(category, "")
        f.write(f"|{count:^5}|"
                f"{operation_date:^15}|"
                f"{transaction_amount:^11}|"
                f"{category_name:^19}| "
                f"{comment}\n")

def get_last_operation_id(log_file: str) -> int:
    """Count the number of lines in the log file and determine the operation 
    number. """
    with open(log_file, "r") as f:
        return sum(1 for _ in f) - 1

def get_current_date() -> str:
    '''Get today date.'''

    return datetime.now().date().strftime('%d-%m-%Y')

def ask_individual_entrepreneurship_status() -> bool:
    '''Ask user if the income is from individual entrepreneurship.'''

    valid_responses = {"да": True, "нет": False}
    while True:
        notify("prompt_income_individual_entrepreneurship")
        user_response = input().strip().lower()
        if user_response in valid_responses:
            return valid_responses[user_response]
        notify("error_input_invalid")


def add_income(is_individual_entrepreneurship: bool, income_amount: str) -> None:
    '''Distribute income between reserve and tax in state file.
    
    If the income is related to individual entrepreneurship ("yes"), add 
    20% of the amount to the tax, and 80% to the reserve.
    If not ("no"), add 100% of the amount to the reserve.
    '''
    while True:
        if is_individual_entrepreneurship == True:
            with open(BUDGET_STATE_FILE,"r") as f:
                state = json.load(f)
                decimal_money = Decimal(income_amount)
                percent20 = Decimal("0.2")
                percent80 = Decimal("0.8")
                reserve_state = Decimal(state["reserve"])
                taxes_state = Decimal(state["taxes"])

                state["reserve"] = str(reserve_state + decimal_money * 
                                       percent80)
                state["taxes"] = str(taxes_state + decimal_money * percent20)
            with open(BUDGET_STATE_FILE, "w") as f:
                json.dump(state, f, indent=4)
            break

        elif is_individual_entrepreneurship == False:
            with open(BUDGET_STATE_FILE,"r") as f:
                state = json.load(f)
                decimal_money = Decimal(income_amount)
                reserve_state2 = Decimal(state["reserve"])
                state["reserve"] = str(reserve_state2 + decimal_money)
            with open(BUDGET_STATE_FILE, "w") as f:
                json.dump(state, f, indent=4)
            break
        else: 
            notify("error_input_invalid")

def handle_user_financial_operations() -> None:
    """Process user financial transactions in an interactive loop."""

    while True:
        notify("prompt_operation_type")
        raw_input = input().strip().lower()

        if raw_input == "menu":
            break
        
        try:
            amount = Decimal(raw_input)
        except InvalidOperation:
            notify("error_input_invalid")
            continue

        if amount == 0:
            notify("error_zero_amount")
            continue
        
        elif raw_input.startswith("+"):
            individual_entrepreneurship_answer = ask_individual_entrepreneurship_status()
            notify("prompt_comment")
            comment = input().strip()
            log_financial_operation(raw_input, "-", comment)
            add_income(individual_entrepreneurship_answer, raw_input)
            return

        elif raw_input.startswith("-"):
            notify("prompt_expense_category")
            user_category = input().strip()
            notify("prompt_comment")
            comment = input()
            log_financial_operation(raw_input, user_category, comment)
            add_expense(raw_input)
            return
        else:
            notify("error_input_invalid")
            continue

def display_financial_state():
    """Run the secondary main loop for working with the account state."""    
    pass

def exit_application() -> None:
    '''Exit the application with a farewell message.'''

    notify("info_exit_message")
    sys.exit()

def wait_for_user_command(
        prompt_key:
        Literal[
            "prompt_start_menu_text"
        ], valid_commands: dict[str, Callable]) -> str:
    """Prompt the user until a valid command is entered.

    :param prompt_key: str - key from the MESSAGES dictionary that defines 
    which message to show before asking for user input.
    :param valid_commands: dict[str, Callable] - A dictionary of valid command 
    strings mapped to callable functions.
    :return: str - The user's input if it matches one of the expected command 
    keys, intended for use in calling the corresponding function.
    """
    valid_inputs = list(valid_commands.keys())
    while True:
        notify(prompt_key)
        user_input = input().strip().lower()
        if user_input in valid_inputs:
            return user_input
        else:
            notify("error_input_invalid")

MENU_OPTIONS = {
    "add": handle_user_financial_operations,
    "balance": display_financial_state,
    "exit": exit_application
}

def main() -> None:
    '''Run the main application loop and route user actions.'''

    while True:
        user_choice = wait_for_user_command("prompt_start_menu_text", MENU_OPTIONS)
        action = MENU_OPTIONS[user_choice]
        action()

if __name__ == "__main__":
    main()