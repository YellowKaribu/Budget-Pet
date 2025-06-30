#!/usr/bin/env python3

#user enter
user_input = input("Введите +доход или -расход")

#input validation
if user_input.startswith("+"):
        while True:
            earning_input = input("Доход с ИП или нет? Да/нет").strip().lower()

            if earning_input == "да":
                #80% add to reserve
                #20% add to taxes
                print("Доход распределен в резервы и налоги")
                break

            elif earning_input == "нет":
                #add to reserve
                print("Доход записан в резервы")
                break

            else: print("Пожалуйста, ответьте да или нет")

elif user_input.startswith("-"):
    while True:
        expence_input = input("Укажите категорию расхода. 1 - еда, 2 - коммуналка, 3 - лекарства, 4 - развлечения, 5 - прочее")
        if expence_input not in ("1", "2", "3", "4", "5"):
            print("Введенное значение неверно.")
        else: break

    #expence_input put to budget_log
    #expence_input subtract from budget_state
    print("Расход учтен")

else: 
     print("Сообщение должно начинаться с - или +")