#!/usr/bin/env python3
from datetime import datetime;
import json
from decimal import Decimal, InvalidOperation

LOG_FILE = "data/budget_log.txt"
STATE_FILE = "data/budget_state.json"
CATEGORIES = {
    "1": "Еда",
    "2": "Коммуналка",
    "3": "Подписки",
    "4": "Развлечения",
    "5": "Прочее"
    }

def write_log(uinput, category, comment):
    today = datetime.now().date().strftime('%d-%m-%Y')
    with open(LOG_FILE,"r") as f:
            counter = sum(1 for _ in f) - 1

    with open(LOG_FILE, "a") as f:
        category_name = CATEGORIES.get(category, "")
        f.write(f"|{counter:^5}|{today:^15}|{uinput:^11}|{category_name:^19}| {comment}\n")
        print(
            "----------------------\n"
            "Операция проведена и записана в лог"
            )

def ip_question():
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

def expence_add(money):
    while True:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            free_state = Decimal(state["free"])
            money_decimal = abs(Decimal(money))
            state["free"] = str(free_state - money_decimal)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
            break


def earning_add(answer, money):
    while True:
        if answer == "yes":
            #80% go to reserves, 20% go to taxes
            with open(STATE_FILE,"r") as f:
                state = json.load(f)
                decimal_money = Decimal(money)
                percent20 = Decimal("0.2")
                percent80 = Decimal("0.8")
                reserve_state = Decimal(state["reserve"])
                taxes_state = Decimal(state["taxes"])

                state["reserve"] = str(reserve_state + decimal_money * percent80)
                state["taxes"] = str(taxes_state + decimal_money * percent20)
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=4)
            break

        elif answer == "no":
            #100% go to reserves
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


def menu_question():
    while True:
        user_input = input(
            "----------------------\n"
            "Для возвращения в меню введите menu\n"
            "Для новой денежной операции введите next: "
        ).strip()  
        if user_input == "menu":
            break

def money_operacions():
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
            write_log(raw_input, "-", comment)
            earning_add(ip_answer, raw_input)

            user_input = input(
                "----------------------\n"
                "Для возвращения в меню введите menu\n"
                "Для новой денежной операции введите что угодно: "
                ).strip()  
            if user_input == "menu":
                break
            else:
                continue

        elif raw_input.startswith("-"):
            user_category = input(
                "----------------------\n"
                "Укажите категорию расхода. 1 - еда, 2 - коммуналка, 3 - лекарства, 4 - развлечения, 5 - прочее: "
                )
            comment = input(
                "----------------------\n"
                "Введите комментарий: "
                )
            write_log(raw_input, user_category, comment)
            expence_add(raw_input)
            user_input = input(
                "----------------------\n"
                "Для возвращения в меню введите menu\n"
                "Для новой денежной операции введите что угодно"
                ).strip()  
            if user_input == "menu":
                break
        else:
            print(
                "----------------------\n"
                "Поставьте + или - перед суммой"
            )
            continue



def state_operacions():
    pass


      
def main():
    while True:
        user_input = input(
            "Введите 1, чтобы добавить расход.\n"
            "ВРЕМЕННО НЕ РАБОТАЕТ!! Введите 2, чтобы посмотреть текущее состояние финансов: "
            )

        if user_input == "1":
            money_operacions()
        elif user_input == "2":
            state_operacions()
        else:
            print("Неверное число.")

if __name__ == "__main__":
    main()