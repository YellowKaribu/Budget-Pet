from typing import List, Dict
from datetime import date
from budgetpet.domain.interfaces import IEventsRepository, ILogger

class MonthlyEventsService():
    def __init__(self, repository: IEventsRepository, logger: ILogger) -> None:
        self.logger = logger
        self.repository = repository


    def get_monthly_events(self) -> List[Dict]:
        try:
            return self.repository.get_monthly_events()
        except Exception as e:
            self.logger.error(f"Error fetching monthly events: {e}")
            raise

    def update_monthly_event(self, event_id: int, last_executed: date) -> None:
        try:
            self.repository.update_monthly_event(event_id, last_executed)
        except Exception as e:
            self.logger.error(f"Error updating monthly event: {e}")
            raise

    def notify_monthly_events(self, statuses: Dict[str, bool]) -> None:
        messages = {
            "pay_rent_status": "29 число — день оплаты аренды.\n"
                                "'Аренда' в балансе обнулена. Не забудьте заплатить арендодателю.\n",
            "make_monthly_calculations": "1 число, месячные пересчеты.\n"
                                        "Прошломесячный доход вычтен из резервов и добавлен в свободные деньги.\n"
                                        "810 из резерва перечислены в аренду. Убедитесь, что отложили деньги."
        }
        for key, value in statuses.items():
            if value:
                self.logger.debug(messages.get(key, f"Событие {key} выполнено."))
