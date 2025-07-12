from ports.output_port import NotifierPort
from config.config import EXPENSE_CATEGORY

class CliNotifierAdapter(NotifierPort):
    def notify_success(self, message: str) -> None:
        print(f"{message}")
    

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