from adapters.cli_input_adapter import CLIInputAdapter
#from adapters.cli_output_adapter import CLIOutputAdapter
#from adapters.console_notifier_adapter import ConsoleNotifierAdapter
from core.use_cases import run_transaction
from core.use_cases import collect_transaction_data
from ports.input_port import TransactionInputPort
from core.exceptions import CancelledTransaction
from config.messages import get_msg_transaction_cancelled

def main():
    input_adapter = CLIInputAdapter()
    #output_adapter = CLIOutputAdapter()
    #notifier_adapter = ConsoleNotifierAdapter()

    while True:
        print("\nВыберите действие:")
        print("1. Добавить транзакцию")
        print("2. Показать баланс")
        print("3. Показать лог операций")
        print("0. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            try:
                tr_data = collect_transaction_data(input_adapter)
            except CancelledTransaction:
                print(get_msg_transaction_cancelled())
                return None
            
            run_transaction(
                input_port=input_adapter,
                output_port=output_adapter,
                notifier_port=notifier_adapter,
                tr_data
            )

        elif choice == "выход":
            print("Выход из программы.")
            break
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