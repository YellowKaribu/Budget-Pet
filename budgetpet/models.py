from enum import Enum
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel

class OperationType(str, Enum):
    INCOME_WITH_TAX = "income_with_tax"
    INCOME_NO_TAX = "income_no_tax"
    EXPENSE = "expense"

class TaxRate(Decimal, Enum):
    TAX = Decimal("0.2")
    RESERVE = Decimal("0.8")

class BudgetState(BaseModel):
    reserve: Decimal
    available_funds: Decimal
    rent: Decimal
    taxes: Decimal

class MonthlyEvent(BaseModel):
    id: int
    name: str
    trigger_day: int
    last_executed: date

class CancelledOperation (Exception):
    pass

class GettingFromDbError(Exception):
    pass

class MonthlyEventDBError(Exception):
    pass

class LoggingError(Exception):
    '''Error when logging operation in database.'''
    pass
from typing import Literal
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Any


class OperationData(BaseModel):
    operation_date: datetime
    operation_type: Literal["income_no_tax", "income_with_tax", "expense"]
    operation_amount: Decimal
    operation_category: int | None = None
    operation_tax_status: Any = "no"
    operation_comment: str | None = None

    def validate(self) -> None:
        if self.operation_amount <= 0:
            raise ValueError("Сумма операции должна быть положительной")

        if self.operation_type == "expense" and not self.operation_category:
            raise ValueError("Категория обязательна для расхода")

        if self.operation_type in ("income_no_tax", "income_with_tax") and self.operation_category:
            raise ValueError("Категория должна быть пустой для дохода")

        if self.operation_type == "expense" and self.operation_tax_status != "no":
            raise ValueError("Флаг 'from_ip' не применим к расходам")


class OperationRecord(OperationData):
    id: int
    operation_type: Literal["income", "expense"]


