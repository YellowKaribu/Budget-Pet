from typing import Tuple
from datetime import datetime
from decimal import Decimal
from budgetpet.domain.interfaces import IOperationsRepository, ILogger

class StatisticService():
    def __init__(self, repository: IOperationsRepository, logger: ILogger) -> None:
        self.logger = logger
        self.repository = repository

        
    def get_last_month_expense_statistic(self) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
        try:
            operations = self.repository.get_operation_history_from_db()
            today = datetime.today()
            food_expense = Decimal("0")
            bills_expense = Decimal("0")
            drugs_expense = Decimal("0")
            games_expense = Decimal("0")
            other_expense = Decimal("0")

            if today.month == 1:
                target_month = 12
            else:
                target_month = today.month - 1

            for tr in operations:
                tr_date = tr.operation_date
                if tr_date.month == target_month and tr.operation_type == "expense":
                    if tr.operation_category == 1:
                        food_expense += Decimal(str(tr.operation_amount))
                    elif tr.operation_category == 2:
                        bills_expense += Decimal(str(tr.operation_amount))
                    elif tr.operation_category == 3:
                        drugs_expense += Decimal(str(tr.operation_amount))
                    elif tr.operation_category == 4:
                        games_expense += Decimal(str(tr.operation_amount))
                    elif tr.operation_category == 5:
                        other_expense += Decimal(str(tr.operation_amount))
            
            total_expense = food_expense + bills_expense + drugs_expense + games_expense + other_expense
            return (food_expense, bills_expense, drugs_expense, games_expense, other_expense, total_expense)
        except Exception as e:
            self.logger.error(f"Error calculating expense statistics: {e}")
            raise
