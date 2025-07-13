from decimal import Decimal
from datetime import datetime, date
from dataclasses import replace, asdict
from core.entities import (
    TransactionType, META_FILE, 
    ParsedTransaction, BudgetState, TransactionInputData
)
from config.config import EXPENSE_CATEGORY
from ports.output_port import BudgetStatePort, NotifierPort, TransactionsLogPort, MetaFilePort
from ports.input_port import TransactionInputPort


def orchestrate_transaction(state_port: BudgetStatePort, log_port: TransactionsLogPort, notifier_port: NotifierPort, transaction_data: TransactionInputData):

    parsed_transaction = parse_transaction_input(transaction_data)
    current_budget_state = state_port.get_state()
    updated_state = apply_transaction_to_state(parsed_transaction, current_budget_state)
    state_port.save_state(updated_state)
    transaction_logging_data = build_log_entry(transaction_data, log_port)
    log_transaction(transaction_logging_data, log_port)
    notifier_port.notify_success("Транзакция добавлена, лог записан.")


def log_transaction(data: dict, log_port: TransactionsLogPort) -> None:
    log_port.write_transaction_log(data)


def build_log_entry(data: TransactionInputData, log_state: TransactionsLogPort) -> dict:
    current_log = log_state.get_transaction_log()
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


def collect_transaction_data(input_port: TransactionInputPort) -> TransactionInputData:
    tr_type = input_port.prompt_transaction_type()
    tr_tax_status = None
    tr_category = None

    if tr_type == "income":
        tr_tax_status = input_port.prompt_tax_status()
    else:
        tr_category = input_port.prompt_transaction_category()
    tr_amount = input_port.prompt_transaction_amount()
    tr_comment = input_port.prompt_transaction_comment()

    return TransactionInputData(
        type=tr_type,
        amount=tr_amount,
        comment=tr_comment,
        category=tr_category,
        tax_status=tr_tax_status,
    )


def show_transactions_log(log_port: TransactionsLogPort, notify_port: NotifierPort):
    log_record = log_port.get_transaction_log()
    notify_port.show_log_record(log_record, EXPENSE_CATEGORY)


def handle_balance():
    pass


def show_budget_balance(output_budget_port: BudgetStatePort, notifier_port: NotifierPort):
    budget_state = output_budget_port.get_state()
    notifier_port.show_budget_state(budget_state)


def check_monthly_events(
        budget_state_port: BudgetStatePort, 
        meta_port: MetaFilePort, 
        notifier_port: NotifierPort
        ):
    pay_rent_status = False
    meta_data = meta_port.get_meta_data(META_FILE)
    today= date.today()

    if should_pay_rent(today, meta_data):
        pay_rent(budget_state_port, meta_port)
        pay_rent_status = True
    #later other events will be added

    all_events_status = {"pay_rent_status": pay_rent_status}

    #if at least 1 event happened, notify user
    if any(all_events_status.values()):
        notifier_port.notify_monthly_events(all_events_status)


def should_pay_rent(today: date, meta_data: dict) -> bool:
    last_rent_pay_str = meta_data["last_rent_pay"]
    last_rent_pay = datetime.strptime(last_rent_pay_str, "%Y-%m-%d").date()

    return (
        today.day >= 13 and (last_rent_pay.month != today.month or 
         last_rent_pay.year != today.year)
        )


def pay_rent(budget_state_port: BudgetStatePort, meta_port: MetaFilePort) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    meta_data = meta_port.get_meta_data(META_FILE)
    #check if already reset
    if meta_data.get("last_rent_pay") == today:
        return

    current_balance = budget_state_port.get_state()
    updated_state = replace(current_balance, rent="0")
    budget_state_port.save_state(updated_state)

    meta_data["last_rent_pay"] = today
    meta_port.save_meta_data(META_FILE, meta_data)
