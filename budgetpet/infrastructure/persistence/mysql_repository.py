from budgetpet.domain.interfaces import IBudgetRepository, IOperationsRepository, IEventsRepository
from budgetpet.domain.models import BudgetState, MonthlyEventDBError, LoggingError, Operation, StatisticFilters
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
        
    def get_operation_by_id(self, operation_data: Operation, cursor) -> Operation:
        query = "SELECT * FROM operations_history WHERE id = %s"

        if cursor is None:
            with get_db_cursor() as cursor:
                cursor.execute(query, (operation_data.id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Operation with id={operation_data.id} not found")
                return map_row_to_record(row) #type: ignore
        
        cursor.execute(query, (operation_data.id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Operation with id={operation_data.id} not found")
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
            operation_data['category'],
            operation_data['tax_rate']
        )
        if cursor is None:
            with get_db_cursor() as cursor:
                cursor.execute(query, values)

        else:
            cursor.execute(query, values)

    def delete_operation(self, operation_data: Operation, cursor) -> None:
        cursor.execute("DELETE FROM operations_history WHERE id = %s", (operation_data.id,))
        if cursor.rowcount == 0:
            raise RuntimeError(f"Operation with id {operation_data.id} not found")
            
    def update_operation(self, new_data: dict, cursor) -> None:
        query = '''
            UPDATE operations_history 
            SET timestamp=%s, type=%s, amount=%s, comment=%s, category=%s, tax_rate=%s
            WHERE id=%s
        '''
        values = (
            new_data['date'],
            new_data['type'],
            new_data['amount'],
            new_data.get('comment'),
            new_data['category'],
            new_data['tax_rate'],
            new_data['id']
        )
        if cursor is None:
            with get_db_cursor() as cursor:
                cursor.execute(query, values)

        else:
            cursor.execute(query, values)

    def get_statistic_from_db(self, user_filters: StatisticFilters) -> List[Any]:
        query = '''
        SELECT category, SUM(amount) as total
        FROM operations_history
        WHERE 1=1
        '''
        params = []

        if user_filters.start_date:
            query += ' AND timestamp >= %s'
            params.append(user_filters.start_date)

        
        if user_filters.end_date:
            query += ' AND timestamp <= %s'
            params.append(user_filters.end_date)


        if user_filters.types:
                placeholders = ','.join(['%s'] * len(user_filters.types))
                query += f" AND type IN ({placeholders})"
                params.extend(user_filters.types)

        if user_filters.categories:
            placeholders = ','.join(['%s'] * len(user_filters.categories))
            query += f" AND category IN ({placeholders})"
            params.extend(user_filters.categories)

        query += " GROUP BY category ORDER BY total DESC"

        with get_db_cursor() as cursor:
                cursor.execute(query, tuple(params))
                return [
                    {'category': row['category'], 'total': str(row['total'])} #type: ignore
                    for row in cursor.fetchall()
                ]
        

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