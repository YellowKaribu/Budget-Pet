from typing import List
from budgetpet.application.use_cases.operations import process_new_operation
from budgetpet.domain.models import DBError, Operation, OperationDTO
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
        try:
            with get_db_cursor() as cursor:
                # Получаем текущее состояние бюджета
                current_budget_state = self.budget_repository.get_current_budget_state()

                # Применяем бизнес-логику к бюджету
                updated_budget_state = process_new_operation(current_budget_state, data)

                # Сохраняем обновлённое состояние бюджета
                self.budget_repository.save_budget_state(updated_budget_state)

                # Формируем словарь для сохранения операции (например, data.model_dump())
                operation_dict = data.model_dump()

                # Сохраняем запись операции в истории
                self.operation_repository.add_operation(operation_dict)

                self.logger.info('Операция добавлена успешно, бюджет обновлён.')

        except Exception as e:
            self.logger.error(f'Ошибка при добавлении операции: {e}')
            raise



    '''def edit_operation(self, operation_id: int, data: dict) -> None:
        try:
            operation = OperationDTO(**data)
            operation.validate()
            self.budget_repository.edit_operation(operation_id, data)
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error editing operation: {e}")
            raise ValueError(str(e))
        except Exception as e:
            self.logger.error(f"Error editing operation: {e}")
            raise

    def delete_operation(self, operation_id: int) -> None:
        try:
            self.repository.delete_operation(operation_id)
        except Exception as e:
            self.logger.error(f"Error deleting operation: {e}")
            raise'''