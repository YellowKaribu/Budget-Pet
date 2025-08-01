from typing import Literal, Optional
from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field, field_validator

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

class DBError(Exception):
    pass

class MonthlyEventDBError(Exception):
    pass

class LoggingError(Exception):
    '''Error when logging operation in database.'''
    pass

class Operation(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: int | None
    date: datetime
    type: Literal['income', 'expense']
    amount: Decimal
    category: str | None
    tax_rate: Decimal = Field(default=Decimal('0'))
    comment: str | None

class OperationDTO(BaseModel):
    id: Optional[int] = None
    date: datetime
    type: Literal['income', 'expense']
    amount: Decimal
    category: Optional[str] = None
    tax_rate: Decimal = Decimal('0')
    comment: Optional[str] = None


    @field_validator("tax_rate", mode="before")
    @classmethod
    def normalize_tax_rate(cls, v):
        if v is None or str(v).strip().lower() in ("", "null"):
            return Decimal(0)
        if float(v) > 100:
            raise ValueError(f"Налог не может быть выше 100")
        try:
            return Decimal(v)
        except Exception:
            raise ValueError(f"Invalid tax_rate: {v}")
        
    @field_validator("date", mode="before")
    @classmethod
    def normalize_date(cls, v):
        if isinstance(v, datetime):
            return v
        if not v:
            return datetime.now()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(v, fmt)
            except ValueError:
                continue
        raise ValueError("Неверный формат даты")
    
    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        if v not in ['income', 'expense']:
            raise ValueError("Неверный тип")
        return v
        
    @field_validator("amount", mode="before")
    @classmethod
    def normalize_amount(cls, v):
        if not v:
            raise ValueError("Нужно ввести сумму")
        try:
            amount = float(v)
        except ValueError:
            raise ValueError("Сумма должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма не может быть 0 или отрицательной")
        return Decimal(str(amount))
    
    def to_domain(self):
        return Operation(
            id=self.id,
            date=self.date,
            type=self.type,
            amount=self.amount,
            category=self.category,
            tax_rate=self.tax_rate,
            comment=self.comment,
        )
    

class StatisticFilters(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    types: list[str] = []
    categories: list[str] = []
