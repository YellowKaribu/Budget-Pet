
from budgetpet.constants import TRANSACTIONS_LOG_PATH, BUDGET_PATH, EXPENSE_CATEGORY
from budgetpet.models import BudgetState, CancelledOperation
import json
import pymysql
import mysql.connector
from dataclasses import asdict
from typing import Any, Literal
from datetime import datetime, date
from decimal import Decimal
from budgetpet.models import (
    OperationData, 
    LoggingError, 
    GettingFromDbError, 
    MonthlyEventDBError, 
    OperationRecord)
from budgetpet.messages import(
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

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'secrets', '.env')
load_dotenv(dotenv_path)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "budget"),
}


def get_current_budget_state() -> BudgetState:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM budget_state LIMIT 1")
    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:
        raise RuntimeError("No budget state found")
    return BudgetState(**row) # type: ignore
    
    
def map_row_to_record(row: dict) -> OperationRecord:
    return OperationRecord(
        id=row["id"],
        operation_date=row["timestamp"],
        operation_type=row["type"],
        operation_amount=row["amount"],
        operation_category=row.get("category"),
        operation_tax_status=row.get("tax_status", "no"),
        operation_comment=row.get("comment")
    )



def get_operation_history() -> list[OperationRecord]:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM operations_history ORDER BY timestamp DESC LIMIT 100")

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [map_row_to_record(row) for row in rows] # type: ignore



def save_budget_state(state: BudgetState) -> None:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    query_update = '''
        UPDATE budget_state SET reserve=%s, available_funds=%s, rent=%s, taxes=%s LIMIT 1
    '''
    values = (state.reserve, state.available_funds, state.rent, state.taxes)

    cursor.execute(query_update, values)

    if cursor.rowcount == 0:
        query_insert = '''
        INSERT INTO budget_state (reserve, available_funds, rent, taxes)
        VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query_insert, values)
    
    connection.commit()
    cursor.close()
    connection.close()


def get_transaction_log() -> list[dict]:
    with open(TRANSACTIONS_LOG_PATH, "r") as f:
        lines = f.readlines()
        entries = [json.loads(line) for line in lines if line.strip()]
        return entries
    

def get_monthly_events() -> list[dict]:
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        query = '''
        SELECT id, trigger_day, last_executed, is_active FROM monthly_events;
        '''
        cursor.execute(query)
        events = cursor.fetchall()

    except GettingFromDbError as e:
        print(f'error: {e}')
        raise

    finally:
        cursor.close()
        connection.close()

    return events # type: ignore


def get_last_month_expense_statistic() -> tuple:
    log_record = get_transaction_log()
    today = datetime.today()

    food_expense = Decimal("0")
    bills_expense = Decimal("0")
    drugs_expense = Decimal("0")
    games_expense = Decimal("0")
    other_expense = Decimal("0")

    if today.month == 1:
        target_month = 12
    else:
        target_month = today.month - 1

    for tr in log_record:
        tr_date = datetime.strptime(tr["timestamp"], "%d-%m-%Y %H:%M:%S")
        if tr_date.month == target_month and tr["type"] == "expense":
            if tr["category"] == 1:
                food_expense += Decimal(str(tr["amount"]))
            elif tr["category"] == 2:
                bills_expense += Decimal(str(tr["amount"]))
            elif tr["category"] == 3:
                drugs_expense += Decimal(str(tr["amount"]))
            elif tr["category"] == 4:
                games_expense += Decimal(str(tr["amount"]))
            elif tr["category"] == 5:
                other_expense += Decimal(str(tr["amount"]))
    
    total_expense = food_expense + bills_expense + drugs_expense + games_expense + other_expense

    return (food_expense, bills_expense, drugs_expense, games_expense, other_expense, total_expense)


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
            raise CancelledOperation()
            
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
            raise CancelledOperation()

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
            raise CancelledOperation()
        print(get_err_invalid_input())


def prompt_transaction_comment() -> str:
        
    user_input = input(get_prompt_comment()).strip()
    if user_input == "отмена":
        raise CancelledOperation()
    
    return user_input


def prompt_tax_status() -> str:
    while True:
        user_input = input(get_prompt_individual_entrepreneurship()).strip().lower()

        if user_input in ("да", "нет"):
            return user_input
        elif user_input == "отмена":
            raise CancelledOperation()
        
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
    print("4. Показать статистику расходов прошлого месяца")
    print("0. Выход")


def notify_exit() -> None:
    print(get_msg_exit())


def notify_invalid_choice() -> None:
    print(get_err_invalid_input())


def notify_success() -> None:
    print(get_msg_success_logged())


def notify_cancel() -> None:
    print (get_msg_transaction_cancelled())


def log_operation(user_data: OperationData) -> None:
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        if user_data.operation_category is None:
            user_data.operation_category = 0


        query_update = '''
        INSERT INTO operations_history (timestamp, type, amount, comment, category, tax_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        values = (
            user_data.operation_date,
            user_data.operation_type,
            user_data.operation_amount,
            user_data.operation_comment,
            user_data.operation_category,
            user_data.operation_tax_status
        )
        print("tax_status value:", user_data.operation_tax_status)

        cursor.execute(query_update, values)
        connection.commit()

    except mysql.connector.Error as e:
        raise LoggingError(f"Ошибка при сохранении лога: {e}")

    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def update_monthly_event(event_id: int, last_executed: date) -> None:
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        query = """
            UPDATE monthly_events
            SET last_executed = %s
            WHERE id = %s
        """
        values = (last_executed, event_id)

        cursor.execute(query, values)
        connection.commit()

    except mysql.connector.Error as e:
        raise MonthlyEventDBError(f"Ошибка при сохранении данных ежемес. ивентов в бд: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

