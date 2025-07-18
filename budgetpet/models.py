from dataclasses import dataclass
from enum import Enum
from typing import Optional
from decimal import Decimal

@dataclass
class LogEntry:
    operation_type: str
    operation_id: int
    operation_date: str
    operation_amount: str
    category: str
    comment: str

@dataclass
class TransactionInputData:
    type: str
    amount: str
    comment: str
    category: Optional[str]
    tax_status: Optional[str]


class TransactionType(Enum):
    INCOME_WITH_TAX = "income_with_tax"
    INCOME_NO_TAX = "income_no_tax"
    EXPENSE = "expense"

class TaxRate(Enum):
    TAX = "0.2"
    RESERVE = "0.8"

@dataclass
class BudgetState():
    reserve: str
    available_funds: str
    rent: str
    taxes: str

@dataclass
class ParsedTransaction():
    type: str
    amount: Decimal

class CancelledTransaction (Exception):
    pass

