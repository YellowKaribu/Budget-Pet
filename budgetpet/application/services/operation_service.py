from typing import List
from budgetpet.application.use_cases.operations import process_new_operation, revert_operation
from budgetpet.domain.models import DBError, Operation
from budgetpet.domain.interfaces import IBudgetRepository, ILogger, IOperationsRepository
from budgetpet.infrastructure.persistence.db_connection import get_db_cursor

class OperationService():
    def __init__(
            self, 
            operation_repository: IOperationsRepository, 
            budget_repository: IBudgetRepository, 
            logger: ILogger
    ):
        self.operation_repository = operation_repository
        self.budget_repository= budget_repository
        self.logger = logger

    def get_operations_history(self) -> List[dict]:
            try:
                return self.operation_repository.get_operation_history_from_db()
            except DBError as e:
                self.logger.error(f"Error fetching operations history: {e}")
                raise

    def add_operation(self, data: Operation) -> None:
        with get_db_cursor() as cursor:
            try:
                current_budget_state = self.budget_repository.get_current_budget_state(cursor)
                updated_budget_state = process_new_operation(current_budget_state, data)
                self.budget_repository.save_budget_state(updated_budget_state, cursor)
                operation_dict = data.model_dump()
                self.operation_repository.add_operation_history(operation_dict, cursor)

                self.logger.info('Операция добавлена успешно, бюджет обновлён.')

            except Exception as e:
                self.logger.error(f'Ошибка при добавлении операции: {e}')
                raise

    def delete_operation(self, operation_data: Operation):
        with get_db_cursor() as cursor:
            operation = self.operation_repository.get_operation_by_id(operation_data, cursor)
            if not operation:
                raise ValueError("Operation not found")

            budget = self.budget_repository.get_current_budget_state(cursor)
            new_budget = revert_operation(budget, operation)
            self.budget_repository.save_budget_state(new_budget, cursor)
            self.operation_repository.delete_operation(operation_data, cursor)

    def edit_operation(self, new_data: Operation) -> None:
        '''Editing an operation means reverting the old operation's impact on the budget and applying the new one'''
        with get_db_cursor() as cursor:
            # Revert the effect of the old operation on the budget
            old_operation = self.operation_repository.get_operation_by_id(new_data, cursor)
            budget = self.budget_repository.get_current_budget_state(cursor)
            new_budget = revert_operation(budget, old_operation)

            # Apply the effect of the new operation to the budget
            updated_budget = process_new_operation(new_budget, new_data)
            self.budget_repository.save_budget_state(updated_budget, cursor)
            dict_data = new_data.model_dump()
            self.operation_repository.update_operation(dict_data, cursor)