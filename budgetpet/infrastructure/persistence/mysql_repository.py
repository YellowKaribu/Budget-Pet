from budgetpet.domain.interfaces import IBudgetRepository, IOperationsRepository, IEventsRepository
from budgetpet.domain.models import BudgetState, MonthlyEventDBError, LoggingError, Operation
from budgetpet.infrastructure.persistence.db_connection import get_db_cursor
from typing import List, Any, Dict
from datetime import date


def map_row_to_record(row: dict) -> Operation:
    return Operation(
        id=row["id"],
        date=row["timestamp"],
        type=row["type"],
        amount=row["amount"],
        category=row.get("category"),
        tax_rate=row.get("tax_rate"), #type: ignore
        comment=row.get("comment")
        )

class MySQLBudgetRepository(IBudgetRepository, IOperationsRepository, IEventsRepository):
    #-------Budget--------
    def save_budget_state(self, state: BudgetState, cursor) -> None:
        query = '''
            UPDATE budget_state
            SET reserve=%s, available_funds=%s, rent=%s, taxes=%s
            LIMIT 1
        '''
        values = (state.reserve, state.available_funds, state.rent, state.taxes)

        if cursor is not None:
            cursor.execute(query, values)
        else:
            with get_db_cursor() as cursor:
                cursor.execute(query, values)


    def get_current_budget_state(self, cursor) -> BudgetState:
        query = "SELECT * FROM budget_state LIMIT 1"

        if cursor is not None:
            cursor.execute(query)
            row = cursor.fetchone()
        else:
            with get_db_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()

        if not row:
            raise RuntimeError("No budget state found")

        return BudgetState(**row)  # type: ignore
        

    #-------Operations--------
    def get_operation_history_from_db(self) -> List[Any]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM operations_history ORDER BY timestamp DESC LIMIT 100")
            rows = cursor.fetchall()
            return [map_row_to_record(row) for row in rows] #type: ignore
        

    def get_operation_by_id(self, operation_id: int, cursor) -> Operation:
        query = "SELECT * FROM operations_history WHERE id = %s"
        cursor.execute(query, (operation_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Operation with id={operation_id} not found")
        return map_row_to_record(row)


    def add_operation_history(self, operation_data: dict, cursor) -> None:
        query = '''
            INSERT INTO operations_history (timestamp, type, amount, comment, category, tax_rate)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        values = (
            operation_data['date'],
            operation_data['type'],
            operation_data['amount'],
            operation_data.get('comment'),
            operation_data.get('category'),
            operation_data.get('tax_rate')
        )
        if cursor is None:
            with get_db_cursor() as cursor:
                cursor.execute(query, values)

        else:
            cursor.execute(query, values)


    def edit_operation(self, operation_id: int, operation_data: dict) -> None:
        with get_db_cursor() as cursor:
            operation_type_for_logging = self._map_type_for_log(operation_data["operation_type"])
            operation_category = operation_data.get("operation_category", 0)
            query = '''
                UPDATE operations_history
                SET timestamp=%s, type=%s, amount=%s, comment=%s, category=%s, tax_status=%s
                WHERE id=%s
            '''
            values = (
                operation_data["operation_date"],
                operation_type_for_logging,
                operation_data["operation_amount"],
                operation_data.get("operation_comment"),
                operation_category,
                operation_data.get("operation_tax_status", "no"),
                operation_id
            )
            try:
                cursor.execute(query, values)
                if cursor.rowcount == 0:
                    raise RuntimeError(f"Operation with id {operation_id} not found")
            except Exception as e:
                raise LoggingError(f"Ошибка при редактировании операции: {e}")


    def delete_operation(self, operation_id: int, cursor) -> None:
        cursor.execute("DELETE FROM operations_history WHERE id = %s", (operation_id,))
        if cursor.rowcount == 0:
            raise RuntimeError(f"Operation with id {operation_id} not found")
            
    #-------Events--------
    def get_monthly_events(self) -> list[dict]:
        with get_db_cursor() as cursor:
            query = '''
                SELECT id, trigger_day, last_executed, is_active FROM monthly_events
            '''
            cursor.execute(query)
            return cursor.fetchall() #type: ignore


    def update_monthly_event(self, event_id: int, last_executed: date) -> None:
        with get_db_cursor() as cursor:
            query = '''
                UPDATE monthly_events
                SET last_executed = %s
                WHERE id = %s
            '''
            values = (last_executed, event_id)
            try:
                cursor.execute(query, values)
            except Exception as e:
                raise MonthlyEventDBError(f"Ошибка при сохранении данных ежемес. ивентов: {e}")


    @staticmethod
    def _map_type_for_log(internal_type: str) -> str:
        type_mapping = {
            "income_with_tax": "income",
            "income_no_tax": "income",
            "expense": "expense"
        }
        return type_mapping.get(internal_type, internal_type)