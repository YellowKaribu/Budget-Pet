from adapters.cli_input_adapter import CLIInputAdapter
from adapters.budget_state_json_adapter import BudgetStateAdapter
from adapters.cli_output_adapter import CliNotifierAdapter
from adapters.transaction_log_jsonl_adapter import TransactionsLoggerJsonl
from core.use_cases import orchestrate_transaction
from core.use_cases import collect_transaction_data
from core.exceptions import CancelledTransaction
from config.messages import get_msg_transaction_cancelled

def main():
    input_port = CLIInputAdapter()
    output_budget_port = BudgetStateAdapter()
    output_log_port = TransactionsLoggerJsonl()
    notifier_port = CliNotifierAdapter()

    

    while True:
        print("\nВыберите действие:")
        print("1. Добавить транзакцию")
        print("2. Показать баланс")
        print("3. Показать лог операций")
        print("0. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            try:
                tr_data = collect_transaction_data(input_port)
            except CancelledTransaction:
                print(get_msg_transaction_cancelled())
                return None
            
            orchestrate_transaction(output_budget_port, output_log_port, notifier_port, tr_data)

        elif choice == "выход":
            print("Выход из программы.")
            continue
        else:
            print("Неверный ввод. Пожалуйста, выберите существующий пункт.")

if __name__ == "__main__":
    main()

"""            handle_transaction(
                input_port=input_adapter,
                output_port=output_adapter,
                notifier_port=notifier_adapter,
                tr_data
            )
        elif choice == "2":
            print("[заглушка] Показ баланса")  # заменить на: show_balance(...)
        elif choice == "3":
            print("[заглушка] Показ лога операций")  # заменить на: show_log(...)"""