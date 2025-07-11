from decimal import Decimal
from datetime import datetime
from dataclasses import replace, asdict
from core.entities import (
    LogEntry, TransactionType, TaxRate, 
    ParsedTransaction, BudgetState, TransactionInputData
)
from config.config import EXPENSE_CATEGORY
from ports.output_port import BudgetStatePort, NotifierPort, TransactionsLogPort
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


def handle_balance():
    pass

def exit_app():
    pass
