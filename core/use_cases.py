from core.entities import LogEntry, TransactionType, TaxRate
from decimal import Decimal
from ports.budget_port import BudgetPort
from ports.input_port import TransactionInputPort
from core.entities import TransactionInputData
from core.exceptions import CancelledTransaction


def run_transaction(input_port, output_port, notifier_port, transaction_data: dict):

    transaction = build_log_entry(transaction_data)

    state = output_port.get_state()
    updated_state = apply_transaction_to_state(transaction, state)

    output_port.save_transaction(transaction)
    output_port.update_state(updated_state)

    notifier_port.notify_success("Транзакция добавлена и счёт обновлён")


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


def apply_income_with_tax(budget_state: dict, transaction: LogEntry) -> dict:
    amount = Decimal(transaction.operation_amount)
    budget_state["reserve"] = str(Decimal(budget_state["reserve"]) + amount * Decimal(TaxRate.RESERVE.value))
    budget_state["taxes"] = str(Decimal(budget_state["taxes"]) + amount * Decimal(TaxRate.TAX.value))
    return budget_state

def apply_income_no_tax(budget_state: dict, transaction: LogEntry) -> dict:
    amount = Decimal(transaction.operation_amount)
    budget_state["reserve"] = str(Decimal(budget_state["reserve"]) + amount)
    return budget_state

def apply_expense(budget_state: dict, transaction: LogEntry) -> dict:
    amount = Decimal(transaction.operation_amount)
    budget_state["available_funds"] = str(Decimal(budget_state["available_funds"]) - amount)
    return budget_state

def process_transaction_type(current_state: dict, transaction: LogEntry) -> dict:
    handlers = {
        TransactionType.INCOME_WITH_TAX.value: apply_income_with_tax,
        TransactionType.INCOME_NO_TAX.value: apply_income_no_tax,
        TransactionType.EXPENSE.value: apply_expense
    }
    handler = handlers.get(transaction.operation_type)
    if not handler:
        raise ValueError(f"Unsupported transaction type: {transaction.operation_type}")
    return handler(current_state, transaction)