from decimal import Decimal
from datetime import datetime, date
from dataclasses import replace, asdict
from models import (
    TransactionType, ParsedTransaction, BudgetState, TransactionInputData
)
from constants import EXPENSE_CATEGORY, META_PATH, BUDGET_PATH, TRANSACTIONS_LOG_PATH
from infrastructure import (
    get_state, save_state, get_transaction_log, get_meta_data, save_meta_data, add_transaction_log
    )

def orchestrate_transaction(transaction_data: TransactionInputData):

    parsed_transaction = parse_transaction_input(transaction_data)
    current_budget_state = get_state()
    updated_state = apply_transaction_to_state(parsed_transaction, current_budget_state)
    save_state(updated_state)
    transaction_logging_data = build_log_entry(transaction_data)
    log_transaction(transaction_logging_data)


def log_transaction(data: dict) -> None:
    add_transaction_log(data)


def build_log_entry(data: TransactionInputData) -> dict:
    current_log = get_transaction_log()
    transaction_id = len(current_log) + 1

    data_to_dict = asdict(data)
    transaction_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    entry = {"id": transaction_id, "timestamp": transaction_date, **data_to_dict}
    return entry


def apply_transaction_to_state(data: ParsedTransaction, state: BudgetState) -> BudgetState:
    if data.type == "income_no_tax":
        updated_reserve = Decimal(state.reserve) + data.amount
        return replace(state, reserve=str(updated_reserve))
    elif data.type == "income_with_tax":
        updated_reserve = Decimal(state.reserve) + data.amount * Decimal("0.8")
        updated_taxes = Decimal(state.taxes) + data.amount * Decimal("0.2")
        return replace(state, reserve=str(updated_reserve), taxes=str(updated_taxes))
    elif data.type == "expense":
        updated_available_funds = Decimal(state.available_funds) - data.amount
        return replace(state, available_funds=str(updated_available_funds))
    else:
        raise ValueError(f"Unknown transaction type: {data.type}")


def parse_transaction_input(transaction_data: TransactionInputData) -> ParsedTransaction:
    new_amount = Decimal(transaction_data.amount.strip())
    normalized_type = transaction_data.type.strip().lower()

    if normalized_type == "income" and transaction_data.tax_status == "да":
        tr_type = TransactionType.INCOME_WITH_TAX
    elif normalized_type == "income" and transaction_data.tax_status == "нет":
        tr_type = TransactionType.INCOME_NO_TAX
    elif normalized_type == "expense":
        tr_type = TransactionType.EXPENSE
    else:
        raise ValueError("Недопустимое сочетание типа и налогового статуса")

    return ParsedTransaction(type=tr_type.value, amount=new_amount)


def check_monthly_events(meta_data: dict, today: date) -> dict[str, bool]:
    events_status = {"pay_rent_status": False, "make_monthly_calculations": False}

    if should_pay_rent(today, meta_data):
        pay_rent()
        events_status["pay_rent_status"] = True

    if should_make_monthly_calculations(today, meta_data):
        monthly_recalculations()
        events_status["make_monthly_calculations"] = True
    return events_status


def should_pay_rent(today: date, meta_data: dict) -> bool:
    last_rent_pay_str = meta_data["last_rent_pay"]
    last_rent_pay = datetime.strptime(last_rent_pay_str, "%Y-%m-%d").date()

    return (
        today.day >= 13 and (last_rent_pay.month != today.month or 
         last_rent_pay.year != today.year)
        )


def pay_rent() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    meta_data = get_meta_data(META_PATH)
    #check if already reset
    if meta_data.get("last_rent_pay") == today:
        return

    current_balance = get_state()
    updated_state = replace(current_balance, rent="0")
    save_state(updated_state)

    meta_data["last_rent_pay"] = today
    save_meta_data(META_PATH, meta_data)


def should_make_monthly_calculations(today: date, meta_data: dict) -> bool:
    last_monthly_calcs_temp = meta_data["last_monthly_recalculations"]
    last_rent_pay = datetime.strptime(last_monthly_calcs_temp, "%Y-%m-%d").date()

    return (
        today.day >= 1 and (last_rent_pay.month != today.month or 
         last_rent_pay.year != today.year)
        )


def monthly_recalculations() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    meta_data = get_meta_data(META_PATH)
    if meta_data.get("last_monthly_recalculations") == today:
        return
    
    current_balance = get_state()
    last_month_income = calculate_last_month_income()
    updated_state = replace(current_balance, rent="810")
    free_funds = updated_state.available_funds 
    updated_state.available_funds = str(Decimal(last_month_income) + Decimal(free_funds))
    updated_state.reserve = str(Decimal(updated_state.reserve) - Decimal(last_month_income))
    updated_state.reserve = str(Decimal(updated_state.reserve) - Decimal("810"))
    save_state(updated_state)

    meta_data["last_monthly_recalculations"] = today
    save_meta_data(META_PATH, meta_data)


def calculate_last_month_income() -> str:
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

    return str(total)
    

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
