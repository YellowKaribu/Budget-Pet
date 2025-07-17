import sys
from constants import EXPENSE_CATEGORY, META_PATH
from models import CancelledTransaction, TransactionInputData
from datetime import date
from infrastructure import (
    get_state,
    get_transaction_log,
    get_meta_data,
    notify_monthly_events,
    prompt_tax_status,
    prompt_transaction_amount,
    prompt_transaction_category,
    prompt_transaction_comment,
    prompt_transaction_type,
    show_budget_state,
    show_log_record,
    show_main_menu,
    notify_exit,
    notify_invalid_choice,
    notify_success,
    notify_cancel
)

from application import (
    check_monthly_events,
    orchestrate_transaction,
    get_last_month_expense_statistic
)

def main():
    '''Entry point.'''
    meta = get_meta_data(META_PATH)
    statuses = check_monthly_events(meta, date.today())
    if any(statuses.values()):
        notify_monthly_events(statuses)

    while True:
        show_main_menu()
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            try:
                tr_data = collect_transaction_data()
            except CancelledTransaction:
                notify_cancel()
                continue
            orchestrate_transaction(tr_data)
            notify_success()
            
        elif choice == "2":
            show_budget_balance()
            continue
            
        elif choice == "3":
            try:
                show_transactions_log()
            except CancelledTransaction:
                notify_cancel()
                continue

        elif choice == "4":
            show_last_month_expense_statictic()
            continue

        elif choice == "0":
            notify_exit()
            sys.exit()
        else:
            notify_invalid_choice()


def collect_transaction_data() -> TransactionInputData:
    tr_type = prompt_transaction_type()
    tr_tax_status = None
    tr_category = None

    if tr_type == "income":
        tr_tax_status = prompt_tax_status()
    else:
        tr_category = prompt_transaction_category()
    tr_amount = prompt_transaction_amount()
    tr_comment = prompt_transaction_comment()

    return TransactionInputData(
        type=tr_type,
        amount=tr_amount,
        comment=tr_comment,
        category=tr_category,
        tax_status=tr_tax_status,
    )


def show_transactions_log():
    log_record = get_transaction_log()
    show_log_record(log_record)


def show_budget_balance():
    budget_state = get_state()
    show_budget_state(budget_state)


def show_last_month_expense_statictic() -> None:
    raw_statistic = get_last_month_expense_statistic()
    statistic_message = (
    f"Траты за прошлый месяц:\n"
    f"  Еда: {raw_statistic[0]}\n"
    f"  Коммуналка: {raw_statistic[1]}\n"
    f"  Лекарства: {raw_statistic[2]}\n"
    f"  Игры: {raw_statistic[3]}\n"
    f"  Другое: {raw_statistic[4]}\n"
    "\n"
    f"Всего: {raw_statistic[5]}"
    )

    print(statistic_message)