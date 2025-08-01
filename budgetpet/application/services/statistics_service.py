from typing import Tuple
from datetime import datetime
from decimal import Decimal
from budgetpet.domain.interfaces import IOperationsRepository, ILogger
from budgetpet.domain.models import StatisticFilters

class StatisticService():
    def __init__(self, repository: IOperationsRepository, logger: ILogger) -> None:
        self.logger = logger
        self.repository = repository

    def get_statistic(self, user_filters: StatisticFilters):
        return self.repository.get_statistic_from_db(user_filters)