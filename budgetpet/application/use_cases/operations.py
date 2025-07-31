
from budgetpet.domain.models import BudgetState, Operation
from decimal import Decimal

def process_new_operation(budget: BudgetState, data: Operation):
    if data.type == "income" and data.tax_rate == Decimal('0'):
        updated_reserve = budget.reserve + data.amount
        return budget.model_copy(update={'reserve': updated_reserve})
        
    elif data.type == "income":
        net_amount = data.amount * (Decimal(100) - data.tax_rate) / Decimal(100)
        tax_amount = data.amount * data.tax_rate / Decimal(100)
        updated_reserve = budget.reserve + net_amount
        updated_taxes = budget.taxes + tax_amount
        return budget.model_copy(update={'reserve': updated_reserve, 'taxes': updated_taxes})
    
    elif data.type == "expense":
        updated_available_funds = budget.available_funds - data.amount
        return budget.model_copy(update={'available_funds': updated_available_funds})
    
    else:
        raise ValueError(f"Unknown transaction type: {data.type}")


def revert_operation(budget: BudgetState, data: Operation) -> BudgetState:
    if data.type == "income" and data.tax_rate == Decimal('0'):
        updated_reserve = budget.reserve - data.amount
        return budget.model_copy(update={'reserve': updated_reserve})

    elif data.type == "income":
        net_amount = data.amount * (Decimal(100) - data.tax_rate) / Decimal(100)
        tax_amount = data.amount * data.tax_rate / Decimal(100)
        updated_reserve = budget.reserve - net_amount
        updated_taxes = budget.taxes - tax_amount
        return budget.model_copy(update={'reserve': updated_reserve, 'taxes': updated_taxes})

    elif data.type == "expense":
        updated_available_funds = budget.available_funds + data.amount
        return budget.model_copy(update={'available_funds': updated_available_funds})

    else:
        raise ValueError(f"Unknown transaction type: {data.type}")
