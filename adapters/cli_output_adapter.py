from ports.output_port import NotifierPort
from config.config import EXPENSE_CATEGORY
from core.entities import BudgetState
from dataclasses import asdict

class CliNotifierAdapter(NotifierPort):
    def notify_success(self, message: str) -> None:
        print(f"{message}")

    def notify_monthly_events(self, monthly_events_statuses: dict) -> None:
        messages ={
            "pay_rent_status": "29 число - день оплаты аренды.\n"\
                "'Аренда' в балансе обнулена. Не забудьте заплатить арендодателю.\n"
        }

        for event_key, status in monthly_events_statuses.items():
            if status:
                message = messages.get(event_key, f"Событие {event_key} выполнено.")
                print (message)

    def show_log_record(self, logs: list[dict], expense_category) -> None:
        display_names = {
            "id": "ID",
            "date": "Дата",
            "type": "Тип",
            "amount": "Сумма",
            "comment": "Коммент",
            "category": "Категория",
            "tax_status": "Налог"
        }

        for i, entry in enumerate(logs, 1):
            parts = []
            for key, display in display_names.items():
                if key in entry:
                    value = entry[key]
                    if key == "category":
                        value = expense_category.get(value, "")
                    parts.append(f"{display}: {value}")
            if parts:
                print(f"{i:02d}. " + " | ".join(parts))
            else:
                print(f"{i:02d}. Запись не содержит известных полей: {entry}")

    def show_budget_state(self, budget_state: BudgetState) -> None:
        display_names = {
        "reserve": "1. Резерв",
        "available_funds": "2. Свободные средства",
        "rent": "3. Аренда",
        "taxes": "4. Отложено на налоги"
        }

        state = asdict(budget_state)
        print ("Ваш текущий баланс:\n")
        for key, value in state.items():
            label = display_names.get(key, key)
            print(f"{label}: {value}")

