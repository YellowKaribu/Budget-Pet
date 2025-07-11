from ports.input_port import TransactionInputPort
from config.config import EXPENSE_CATEGORY
from config.messages import (
    get_prompt_transaction_type,
    get_err_invalid_input,
    get_prompt_amount,
    get_err_zero_amount,
    get_err_empty_input,
    get_err_input_not_a_number,
    get_prompt_transaction_category,
    get_prompt_comment,
    get_prompt_individual_entrepreneurship
)
from typing import Literal
from core.exceptions import CancelledTransaction

class CLIInputAdapter(TransactionInputPort):
    def prompt_transaction_type(self) -> Literal["expense", "income"]:
        """
        Prompt the user to choose a transaction type:
        '+' for income (with or without tax, clarified via a follow-up question),
        '-' for expense.
        """

        while True:
            user_input_type = input(get_prompt_transaction_type()).strip().lower()

            if user_input_type == "+":
                return "income"
            elif user_input_type == "-":
                return "expense"
            elif user_input_type == "отмена":
                raise CancelledTransaction()
                
            print(get_err_invalid_input())


    def prompt_transaction_amount(self) -> str:
        while True:
            input_amount = input(get_prompt_amount()).strip()
            # Replace comma with dot to support European number format (e.g., "1,2" → "1.2")
            validated_input_amount = input_amount.replace(",", ".")

            if not validated_input_amount:
                print(get_err_empty_input())
                continue

            elif input_amount == "отмена":
                raise CancelledTransaction()

            try:
                amount = float(validated_input_amount)
                if amount == 0:
                    print(get_err_zero_amount())
                    continue
                return validated_input_amount
            except ValueError:
                print(get_err_input_not_a_number())
                continue


    def prompt_transaction_category(self) -> str:
        while True:
            user_input = input(get_prompt_transaction_category()).strip()

            if user_input in EXPENSE_CATEGORY:
                return user_input
            elif user_input == "отмена":
                raise CancelledTransaction()
            print(get_err_invalid_input())

    
    def prompt_transaction_comment(self) -> str:
            
        user_input = input(get_prompt_comment()).strip()
        if user_input == "отмена":
            raise CancelledTransaction()
        
        return user_input


    def prompt_tax_status(self) -> str:
        while True:
            user_input = input(get_prompt_individual_entrepreneurship()).strip().lower()

            if user_input in ("да", "нет"):
                return user_input
            elif user_input == "отмена":
                raise CancelledTransaction()
            
            print(get_err_invalid_input())

