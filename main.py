from budgetpet.infrastructure.logging.logger import AppLogger
from budgetpet.infrastructure.persistence.mysql_repository import MySQLBudgetRepository
from budgetpet.application.services.budget_service import BudgetService
from budgetpet.application.services.operation_service import OperationService
from budgetpet.application.services.statistics_service import StatisticService

from budgetpet.interface.web_api import create_app

def main():
    repo = MySQLBudgetRepository()
    budget_repo = MySQLBudgetRepository() 
    operations_repo = MySQLBudgetRepository()
    events_repo = MySQLBudgetRepository()
    logger = AppLogger()
    budget_service = BudgetService(budget_repo, logger)
    operations_service = OperationService(operations_repo, budget_repo, logger)
    statistic_service = StatisticService(repo, logger)
    services = {
        'budget': budget_service,
        'statistic': statistic_service,
        'operations': operations_service
    }

    app = create_app(services)
    app.run(debug=True)

if __name__ == '__main__':
    main()
