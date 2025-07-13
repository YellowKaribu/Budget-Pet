from decimal import Decimal
from datetime import datetime, date
from dataclasses import replace, asdict
from models import (
    TransactionType, ParsedTransaction, BudgetState, TransactionInputData
)
from constants import EXPENSE_CATEGORY, META_PATH
from infrastructure import (
    get_state, save_state, get_transaction_log, get_meta_data, save_meta_data, write_transaction_log
    )

def orchestrate_transaction(transaction_data: TransactionInputData):

    parsed_transaction = parse_transaction_input(transaction_data)
    current_budget_state = get_state()
    updated_state = apply_transaction_to_state(parsed_transaction, current_budget_state)
    save_state(updated_state)
    transaction_logging_data = build_log_entry(transaction_data)
    log_transaction(transaction_logging_data)


def log_transaction(data: dict) -> None:
    write_transaction_log(data)


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
    events_status = {"pay_rent_status": False}

    if should_pay_rent(today, meta_data):
        pay_rent()
        events_status["pay_rent_status"] = True
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