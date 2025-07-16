from constants import TRANSACTIONS_LOG_PATH, BUDGET_PATH, EXPENSE_CATEGORY
from models import BudgetState, CancelledTransaction
import json
from dataclasses import asdict
from typing import Any, Literal

from messages import(
    get_err_empty_input,
    get_err_input_not_a_number,
    get_err_invalid_input,
    get_err_zero_amount,
    get_msg_exit,
    get_msg_success_logged,
    get_msg_transaction_cancelled,
    get_prompt_amount,
    get_prompt_comment,
    get_prompt_individual_entrepreneurship,
    get_prompt_menu,
    get_prompt_transaction_category,
    get_prompt_transaction_type
)

def get_state() -> BudgetState:
    with open(BUDGET_PATH, "r") as f:
        data = json.load(f)
        return BudgetState(**data)
    

def save_state(state: BudgetState) -> None:
    with open(BUDGET_PATH, "w") as f:
        json.dump(asdict(state), f, indent=2)


def get_transaction_log() -> list[dict]:
    with open(TRANSACTIONS_LOG_PATH, "r") as f:
        lines = f.readlines()
        entries = [json.loads(line) for line in lines if line.strip()]
        return entries
    

def add_transaction_log(entry: dict) -> None:
    with open(TRANSACTIONS_LOG_PATH, "a") as f:
        json.dump(entry, f)
        f.write("\n")


def get_meta_data(path: str) -> dict:
    data = load_json(path)
    return validate_meta_data(data)


def save_meta_data(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise ValueError("Meta file contains incorrect JSON.")


def validate_meta_data(data: Any) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Incorrect meta file data type.")
    return data


def notify_monthly_events(statuses: dict[str, bool]) -> None:
    messages = {
        "pay_rent_status": "29 число — день оплаты аренды.\n" \
        "'Аренда' в балансе обнулена. Не забудьте заплатить арендодателю.\n",
        "make_monthly_calculations": "1 число, месячные пересчеты.\n" \
        "Прошломесячный доход вычтен из резервов и добавлен в свободные деньги.\n" \
        "810 из резерва перечислены в аренду. Убедитесь, что отложили деньги."
    }
    for key, value in statuses.items():
        if value:
            print(messages.get(key, f"Событие {key} выполнено."))


def prompt_transaction_type() -> Literal["expense", "income"]:
    """
    Prompt the user to choose a transaction type:
    '+' for income (with or without tax, clarified via a follow-up question),
    '-' for expense.
    """

    while True:
        user_input_type = input(get_prompt_transaction_type()).strip().lower()

        if user_input_type == "+":
            return "income"
        elif user_input_type == "-":
            return "expense"
        elif user_input_type == "отмена":
            raise CancelledTransaction()
            
        print(get_err_invalid_input())


def prompt_transaction_amount() -> str:
    while True:
        input_amount = input(get_prompt_amount()).strip()
        # Replace comma with dot to support European number format (e.g., "1,2" → "1.2")
        validated_input_amount = input_amount.replace(",", ".")

        if not validated_input_amount:
            print(get_err_empty_input())
            continue

        elif input_amount == "отмена":
            raise CancelledTransaction()

        try:
            amount = float(validated_input_amount)
            if amount == 0:
                print(get_err_zero_amount())
                continue
            return validated_input_amount
        except ValueError:
            print(get_err_input_not_a_number())
            continue


def prompt_transaction_category() -> str:
    while True:
        user_input = input(get_prompt_transaction_category()).strip()

        if user_input in EXPENSE_CATEGORY:
            return user_input
        elif user_input == "отмена":
            raise CancelledTransaction()
        print(get_err_invalid_input())


def prompt_transaction_comment() -> str:
        
    user_input = input(get_prompt_comment()).strip()
    if user_input == "отмена":
        raise CancelledTransaction()
    
    return user_input


def prompt_tax_status() -> str:
    while True:
        user_input = input(get_prompt_individual_entrepreneurship()).strip().lower()

        if user_input in ("да", "нет"):
            return user_input
        elif user_input == "отмена":
            raise CancelledTransaction()
        
        print(get_err_invalid_input())


def show_budget_state(budget_state: BudgetState) -> None:
    display_names = {
    "reserve": "1. Резерв",
    "available_funds": "2. Свободные средства",
    "rent": "3. Аренда",
    "taxes": "4. Отложено на налоги"
    }

    state = asdict(budget_state)
    print ("Ваш текущий баланс:\n")
    for key, value in state.items():
        label = display_names.get(key, key)
        print(f"{label}: {value}")


def show_log_record(logs: list[dict]) -> None:
    display_names = {
        "id": "ID",
        "date": "Дата",
        "type": "Тип",
        "amount": "Сумма",
        "comment": "Коммент",
        "category": "Категория",
        "tax_status": "Налог"
    }

    for i, entry in enumerate(logs, 1):
        parts = []
        for key, display in display_names.items():
            if key in entry:
                value = entry[key]
                if key == "category":
                    value = EXPENSE_CATEGORY.get(value, "")
                parts.append(f"{display}: {value}")
        if parts:
            print(f"{i:02d}. " + " | ".join(parts))
        else:
            print(f"{i:02d}. Запись не содержит известных полей: {entry}")


def show_main_menu() -> None:
    print("\nВыберите действие:")
    print("1. Добавить транзакцию")
    print("2. Показать баланс")
    print("3. Показать лог операций")
    print("0. Выход")


def notify_exit() -> None:
    print(get_msg_exit())


def notify_invalid_choice() -> None:
    print(get_err_invalid_input())


def notify_success() -> None:
    print(get_msg_success_logged())


def notify_cancel() -> None:
    print (get_msg_transaction_cancelled())