from decimal import Decimal
from budgetpet.logger import logger
from typing import Literal, cast
from datetime import datetime, date, time
from budgetpet.models import (
    OperationType, BudgetState, OperationData, TaxRate, LoggingError, MonthlyEvent
)
from budgetpet.constants import EXPENSE_CATEGORY, META_PATH, BUDGET_PATH, TRANSACTIONS_LOG_PATH
from budgetpet.infrastructure import (
    get_current_budget_state, save_budget_state, 
    get_transaction_log, get_monthly_events, save_meta_data, 
    log_operation, update_monthly_event
    )

def process_new_operation(user_data: dict):
    logger.debug('Ядро начало обработку операции со следующими данными: %s', user_data)

    try:
        logger.debug('Начата валидация данных.')
        validated_data = validate_user_data(user_data)
    except ValueError as e:
        logger.warning('Ошибка валидации данных, полученных в оркестратор операций: %s', e)
        raise
    
    try:
        logger.debug('Начато выполнение расчетов и запись в бд бюджета. ')
        current_budget_state = get_current_budget_state()
        updated_state = apply_operation_to_budget(validated_data, current_budget_state)
        save_budget_state(updated_state)
    except Exception as e:
        logger.error('Ошибка выполнения операции с бюджетом: %s', e)
        raise

    try:
        logger.debug('Начато добавление в историю операций.')
        log_operation(validated_data)
    except LoggingError as e:
        logger.error('Ошибка записи истории операций: %s', e)
        raise

    logger.info('Операция выполнена и записана успешно')


def apply_operation_to_budget(data: OperationData, state: BudgetState) -> BudgetState:

    if data.operation_type == "income_no_tax":
        updated_reserve = state.reserve + data.operation_amount
        return state.model_copy(update={'reserve': updated_reserve})
    
    elif data.operation_type == "income_with_tax":
        updated_reserve = state.reserve + data.operation_amount * TaxRate.RESERVE
        updated_taxes = state.taxes + data.operation_amount * TaxRate.TAX
        return state.model_copy(update={'reserve': updated_reserve, 'taxes': updated_taxes})
    
    elif data.operation_type == "expense":
        updated_available_funds = state.available_funds - data.operation_amount
        return state.model_copy(update={'available_funds': updated_available_funds})
    
    else:
        raise ValueError(f"Unknown transaction type: {data.operation_type}")


def parse_operation_date(date_str: str | None) -> datetime:
    if not date_str:
        return datetime.now()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    raise ValueError("Неверный формат даты")


def normalize_tax_status(value) -> str:
    if value is None:
        return "no"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, str):
        val = value.lower()
        if val in ("yes", "no"):
            return val
    return "no"


def parse_operation_type_and_tax(
    type_str: str, tax_str: str
) -> tuple[
    Literal["income_no_tax", "income_with_tax", "expense"], str
]:
    tax_str = normalize_tax_status(tax_str)
    type_str = type_str.strip().lower()

    if type_str == "income":
        if tax_str == "yes":
            return "income_with_tax", "yes"
        if tax_str == "no":
            return "income_no_tax", "no"
        raise ValueError("Недопустимый налоговый статус для дохода")
    elif type_str == "expense":
        return "expense", "no"

    raise ValueError("Недопустимый тип транзакции")


def validate_user_data(transaction_data: dict) -> OperationData:

    operation_date = parse_operation_date(transaction_data.get('operation_date'))
    operation_type, tax_status = parse_operation_type_and_tax(
        transaction_data.get('type', ''),
        transaction_data.get('tax_status', '')
    )

    amount = Decimal(str(transaction_data.get('amount', '')).strip())
    category = transaction_data.get('category')
    comment = transaction_data.get('comment', '')

    return OperationData(
        operation_date=operation_date,
        operation_type=operation_type,
        operation_amount=amount,
        operation_category=category,
        operation_tax_status=tax_status,
        operation_comment=comment
    )


def check_day_of_monthly_events(events: list[dict]) -> list:
    today = date.today()
    events_to_run = []

    for event in events:
        if today.day < event['trigger_day']:
            continue

        last_executed = cast(date, event['last_executed'])
        if last_executed is None:
            events_to_run.append(event['id'])
            continue

        if last_executed.year != today.year or last_executed.month != today.month:
            events_to_run.append(event['id'])
    
    return events_to_run


def run_monthly_event(events_to_run: list) -> None:
    if events_to_run == 1:
        pay_rent(events_to_run)
    elif events_to_run == 2:
        monthly_recalculations(events_to_run)


def should_run_monthly_event() -> None:
    try:
        events_data = get_monthly_events()
        events_to_run = check_day_of_monthly_events(events_data)
        if events_to_run:
            run_monthly_event(events_to_run)
    #временная заглушка, пока не введен логгинг
    except Exception as e:
        logger.error('Ошибка при проверке ежемесячных ивентов: %s', e)
        raise


def pay_rent(event_id) -> None:
    current_balance = get_current_budget_state()
    updated_state = current_balance.model_copy(update={'operation_rent': Decimal('0')})
    save_budget_state(updated_state)

    last_executed_update = date.today()
    update_monthly_event(event_id, last_executed_update)


def monthly_recalculations(event_id) -> None:
    current_balance = get_current_budget_state()

    #Take rent money from 'reserve' and add to 'rent'
    updated_state = current_balance.model_copy(update={"rent": Decimal("810")})
    updated_state.reserve = updated_state.reserve - Decimal("810")

    #Add last month earnings amount to free money (from reserve)
    last_month_income = calculate_last_month_income()
    free_funds = updated_state.available_funds 
    updated_state.available_funds = last_month_income + free_funds
    updated_state.reserve = updated_state.reserve - last_month_income
    save_budget_state(updated_state)

    last_executed_update = date.today()
    update_monthly_event(event_id, last_executed_update)


def calculate_last_month_income() -> Decimal:
    log_record = get_transaction_log()
    total = Decimal("0")
    today = datetime.today()

    #check if it's januar
    if today.month == 1:
        target_month = 12
        target_year = today.year - 1
    else:
        target_month = today.month - 1
        target_year = today.year

    #parcing log file for previous transactions
    for tr in log_record:
        tr_date = datetime.strptime(tr["timestamp"], "%d-%m-%Y %H:%M:%S")
        if tr_date.year == target_year and tr_date.month == target_month and tr["type"] == "income":
            total += Decimal(str(tr["amount"]))

    return Decimal(total) * Decimal ('0.8')
    
