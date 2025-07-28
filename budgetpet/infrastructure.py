
from budgetpet.models import BudgetState
import mysql.connector
from budgetpet.db import db_cursor
from typing import Any
from datetime import datetime, date
from decimal import Decimal
from budgetpet.models import (
    OperationData, 
    LoggingError, 
    GettingFromDbError, 
    MonthlyEventDBError, 
    OperationRecord)

from budgetpet.logger import logger


def get_current_budget_state(cursor) -> BudgetState:

    cursor.execute("SELECT * FROM budget_state LIMIT 1")
    row = cursor.fetchone()

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
    
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM operations_history ORDER BY timestamp DESC LIMIT 100")
            rows = cursor.fetchall()
            return [map_row_to_record(row) for row in rows] # type: ignore

    except Exception as e:
        logger.error('Ошибка при получении истории операций: %s', e)
        raise


def save_budget_state(state: BudgetState, cursor) -> None:
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
    

def get_monthly_events() -> list[dict]:

    query = '''
    SELECT id, trigger_day, last_executed, is_active FROM monthly_events;
    '''
    try:
        with db_cursor() as cursor:
            cursor.execute(query)
            events = cursor.fetchall()
            return events # type: ignore

    except GettingFromDbError as e:
        logger.error('Ошибка при получении списка ежемес. ивентов из бд: %s', e)
        raise


def get_last_month_expense_statistic() -> tuple:
    log_record = get_operation_history()
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
        tr_date = tr.operation_date
        if tr_date.month == target_month and tr.operation_type == "expense":
            if tr.operation_category == 1:
                food_expense += Decimal(str(tr.operation_amount))
            elif tr.operation_category == 2:
                bills_expense += Decimal(str(tr.operation_amount))
            elif tr.operation_category == 3:
                drugs_expense += Decimal(str(tr.operation_amount))
            elif tr.operation_category == 4:
                games_expense += Decimal(str(tr.operation_amount))
            elif tr.operation_category == 5:
                other_expense += Decimal(str(tr.operation_amount))
    
    total_expense = food_expense + bills_expense + drugs_expense + games_expense + other_expense

    return (food_expense, bills_expense, drugs_expense, games_expense, other_expense, total_expense)


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


def map_type_for_log(internal_type: str) -> str:
    type_mapping = {
        "income_with_tax": "income",
        "income_no_tax": "income",
        "expense": "expense"
    }
    return type_mapping.get(internal_type, internal_type)


def log_operation(user_data: OperationData, cursor) -> None:
    try:
        if user_data.operation_category is None:
            user_data.operation_category = 0

        operation_type_for_logging = map_type_for_log(user_data.operation_type)

        query_update = '''
        INSERT INTO operations_history (timestamp, type, amount, comment, category, tax_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        values = (
            user_data.operation_date,
            operation_type_for_logging,
            user_data.operation_amount,
            user_data.operation_comment,
            user_data.operation_category,
            user_data.operation_tax_status
        )
        cursor.execute(query_update, values)

    except mysql.connector.Error as e:
        raise LoggingError(f"Ошибка при сохранении лога: {e}")


def update_monthly_event(event_id: int, last_executed: date) -> None:
    try:
        with db_cursor() as cursor:

            query = """
                UPDATE monthly_events
                SET last_executed = %s
                WHERE id = %s
            """
            values = (last_executed, event_id)

            cursor.execute(query, values)

    except mysql.connector.Error as e:
        raise MonthlyEventDBError(f"Ошибка при сохранении данных ежемес. ивентов в бд: {e}")
