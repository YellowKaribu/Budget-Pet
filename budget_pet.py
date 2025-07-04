#!/usr/bin/env python3
from datetime import datetime;
import json
from decimal import Decimal, InvalidOperation
from typing import Callable #for dicts
import sys #for sys.exit()


LOG_FILE = "data/budget_log.txt"
STATE_FILE = "data/budget_state.json"
EXPENSE_CATEGORIES = {
    "1": "Еда",
    "2": "Коммуналка",
    "3": "Подписки",
    "4": "Развлечения",
    "5": "Прочее"
    }
MENU_START_TEXT = (
    "----------------------\n"
    "Введите add, чтобы добавить расход/доход.\n"
    "Введите balance, чтобы посмотреть текущее состояние финансов "
    "(ВРЕМЕННО НЕ РАБОТАЕТ)\n"
    "Введите exit, чтобы закрыть программу\n"
    "Ваш ввод: "
)

def log_user_operacion(raw_input: str, category: str, comment: str) -> None:
    """Append a formatted user operation to the log file and print 
    confirmation message.

    :param raw_input: str - user input representing an amount, with a sign 
    indicating expense or earning (e.g. "-500").
    :param category: str - user input number representing the expense category.
    :param comment: str - optional user comment to describe the operation.
    :return: None - write to log file and print a confirmation message.
    """

    today = get_today_date()
    counter = get_log_line_number(LOG_FILE)

    write_line_in_logfile(LOG_FILE, 
                          counter, 
                          today, 
                          raw_input, 
                          category, 
                          comment)
    print(
        "----------------------\n"
        "Операция проведена и записана в лог"
    )

def write_line_in_logfile(
    log_file: str, 
    count: int, 
    today_date: str, 
    money_input: str, 
    category: str, 
    comment: str
) -> None:
    """Write a line in the log file with user input parameters.

    :param log_file: str - path to the log file.
    :param count: str - number of operacion.
    :param today_date: str - today date which is counts with separate function.
    :param money_input: str - user input representing an amount and what it is 
    - expence or earning (e.g. "-500").
    :param category: str - user input as number indicating the expense category 
    (e.g. "food").
    :param comment: str - optional user comment to describe the operation 
    (e.g. "lunch").
    :return: None - write a line to log file
    """
    
    with open(log_file, "a") as f:
        category_name = EXPENSE_CATEGORIES.get(category, "")
        f.write(f"|{count:^5}|"
                f"{today_date:^15}|"
                f"{money_input:^11}|"
                f"{category_name:^19}| "
                f"{comment}\n")

def get_log_line_number(log_file: str) -> int:
    """Count the number of lines in the log file and determine the operation 
    number.

    :param log_file: str - path to the log file.
    :return: int - number of user operation.
    """
    with open(log_file, "r") as f:
        return sum(1 for _ in f) - 1

def get_today_date() -> str:
    '''Get today date.
    
    :return: str - today date.
    '''
    return datetime.now().date().strftime('%d-%m-%Y')

def ip_question() -> str:
    '''Ask user if the income is from individual entrepreneurship.

    :return: str - answer yes or no as string.
    '''
    while True:
        user_input = input(
            "----------------------\n"
            "Доход с ИП? Ответ должен быть в формате + или -: "
            ).strip()
        if user_input == "+":
            return "yes"
        elif user_input == "-":
            return "no"
        else: 
            print(
                "----------------------\n"
                "Ввод неверен."
                )

def expense_add(money: str) -> None:
    '''Subtract the expense amount from the free balance in the state file.
    
    :param money: str - expense amount entered by user.
    :return: None - modifies the state file in place.
    '''
    while True:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            free_state = Decimal(state["free"])
            money_decimal = abs(Decimal(money))
            state["free"] = str(free_state - money_decimal)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
            break


def earning_add(answer: str, money: str) -> None:
    '''Distribute income between reserve and tax in state file.

    :param answer: str - user response to whether the income is from individual 
    entrepreneurship ("yes" or "no").
    :param money: str - the total income amount entered by the user (expected 
    to be convertible to Decimal).
    :return: None - updates state file in place.

    If the income is related to individual entrepreneurship ("yes"), add 
    20% of the amount to the tax, and 80% to the reserve.
    If not ("no"), add 100% of the amount to the reserve.
    '''
    while True:
        if answer == "yes":
            with open(STATE_FILE,"r") as f:
                state = json.load(f)
                decimal_money = Decimal(money)
                percent20 = Decimal("0.2")
                percent80 = Decimal("0.8")
                reserve_state = Decimal(state["reserve"])
                taxes_state = Decimal(state["taxes"])

                state["reserve"] = str(reserve_state + decimal_money * 
                                       percent80)
                state["taxes"] = str(taxes_state + decimal_money * percent20)
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=4)
            break

        elif answer == "no":
            with open(STATE_FILE,"r") as f:
                state = json.load(f)
                decimal_money = Decimal(money)
                reserve_state2 = Decimal(state["reserve"])
                state["reserve"] = str(reserve_state2 + decimal_money)
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=4)
            break
        else: 
            print(
                "----------------------\n"
                "Ответ на ИП-вопрос некорректен."
                )

def money_operations() -> None:
    """Main loop, handle user-entered operations in an interactive loop.

    :return: None - runs interactively until the user exits to menu.

    Accepts user input in the format "+amount" for earnings or "-amount" for 
    expenses.
    - Validates the input as a signed decimal number.
    - For income, asks if it is from individual entrepreneurship, logs it, 
    and distributes funds.
    - For expenses, asks for a category and comment, logs it, and subtracts 
    from the balance.
    - Allows the user to return to the main menu at any time by typing 'menu'.
    """
    while True:
        raw_input = input(
            "----------------------\n"
            "Чтобы ввести доход, введите +сумма \n" 
            "Чтобы ввести расход, введите -сумма \n" 
            "Чтобы выйти в главное меню, введите menu: "
        ).strip().lower()

        if raw_input == "menu":
            break
        
        try:
            amount = Decimal(raw_input)
        except InvalidOperation:
            print(
                "----------------------\n"
                "Введите число со знаком - или +, иные символы недопустимы."
                )
            continue

        if amount == 0:
            print(
                "----------------------\n"
                "Сумма ввода не может быть равна 0"
                )
            continue
        
        elif raw_input.startswith("+"):
            ip_answer = ip_question()
            comment = input(
                "----------------------\n"
                "Введите комментарий: "
                )
            log_user_operacion(raw_input, "-", comment)
            earning_add(ip_answer, raw_input)
            return

        elif raw_input.startswith("-"):
            user_category = input(
                "----------------------\n"
                "Укажите категорию расхода. 1 - еда, 2 - коммуналка, " \
                "3 - лекарства, 4 - развлечения, 5 - прочее: "
                )
            comment = input(
                "----------------------\n"
                "Введите комментарий: "
                )
            log_user_operacion(raw_input, user_category, comment)
            expense_add(raw_input)
            return
        else:
            print(
                "----------------------\n"
                "Поставьте + или - перед суммой"
            )
            continue

def state_operations():
    """Run the secondary main loop for working with the account state.

    :return: None - to be implemented.

    This function will handle non-transactional state operations, such as 
    reviewing, adjusting, or resetting the balance and reserves.
    """    
    pass

def exit_program() -> None:
    '''Exit the program with a farewell message.
    :return: None - it`s just exit from programm.
    '''

    print(
        "----------------------\n"
        "Выход из программы. До свидания!"    
    )
    sys.exit()

def wait_for_command(prompt: str, expected: dict[str, Callable]) -> str:
    """Prompt the user until a valid command is entered.

    :param prompt: str - Text displayed to the user before input.
    :param expected: dict[str, Callable] - A dictionary of valid command 
    strings mapped to callable functions.
    :return: str - The user's input if it matches one of the expected command 
    keys, intended for use in calling the corresponding function.

    This function takes an input prompt and a dictionary where each key is a 
    valid user command and each value is the function to be called when that 
    command is selected. By using this dictionary-based structure, you can 
    easily change or extend the available commands by modifying the dictionary 
    alone, without changing this function. The dictionaries are located above 
    the main function.
    """
    valid_inputs = list(expected.keys())
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in valid_inputs:
            return user_input
        else:
            print(
                "----------------------\n"
                "Неверный ввод. Попробуйте ещё раз."
            )

MENU_OPTIONS = {
    "add": money_operations,
    "balance": state_operations,
    "exit": exit_program
}

def main() -> None:
    '''Start the main program loop and route user to available actions.

    :return: None - runs until terminated by the user (e.g., Ctrl+C).
    '''
    while True:
        choice_key = wait_for_command(MENU_START_TEXT, MENU_OPTIONS)
        user_choice = MENU_OPTIONS[choice_key]
        user_choice()

if __name__ == "__main__":
    main()