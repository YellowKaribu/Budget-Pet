#!/usr/bin/env python3
from datetime import datetime;

#user enter
user_input = input("Введите +доход или -расход: ")
today = datetime.now().date().strftime('%d-%m-%Y')
expence_categories = {'1':"Еда",'2':"Коммуналка",'3':"Лекарства",'4':"Развлечения",'5':"Прочее"}

#input validation
if user_input.startswith("+"):
        while True:
            earning_input = input("Доход с ИП или нет? Да/нет: ").strip().lower()

            if earning_input == "да":
                #80% add to reserve
                #20% add to taxes
                comment = input("Ваш комментарий: ")
                with open("data/budget_log.txt","r+") as f:
                    counter = sum(1 for _ in f) - 1
                    f.write(f"|{counter:^5}|{today:^15}|{user_input:^11}|{"": ^19}| {comment}\n")
                print("Доход распределен в резервы и налоги")
                break

            elif earning_input == "нет":
                #add to reserve
                comment = input("Ваш комментарий: ")
                with open("data/budget_log.txt","r+") as f:
                    counter = sum(1 for _ in f) - 1
                    f.write(f"|{counter:^5}|{today:^15}|{user_input:^11}|{"": ^19}| {comment}\n")
                                  
                print("Доход записан в резервы")
                break

            else: 
                print("Пожалуйста, ответьте да или нет")

elif user_input.startswith("-"):
    while True:
        expence_input = input("Укажите категорию расхода. 1 - еда, 2 - коммуналка, 3 - лекарства, 4 - развлечения, 5 - прочее: ")
        if expence_input not in ("1", "2", "3", "4", "5"):
            print("Введенное значение неверно.")
        else: 
            category = expence_categories.get(expence_input)
            comment = input("Ваш комментарий: ")
            with open("data/budget_log.txt","r+") as f:
                counter = sum(1 for _ in f) - 1
                f.write(f"|{counter:^5}|{today:^15}|{user_input:^11}|{category: ^19}| {comment}\n")    
                print("Расход распределен в резервы и налоги")
                break
    #expence_input subtract from budget_state

else: 
    print("Сообщение должно начинаться с - или +")