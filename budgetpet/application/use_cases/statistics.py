def calculate_last_month_income() -> Decimal:
    log_record = get_operation_history()
    total = Decimal("0")
    today = datetime.today()

    # Определение предыдущего месяца и года
    if today.month == 1:
        target_month = 12
        target_year = today.year - 1
    else:
        target_month = today.month - 1
        target_year = today.year

    # Проход по операциям и суммирование доходов за прошлый месяц
    for tr in log_record:
        tr_date = tr.operation_date
        if tr_date.year == target_year and tr_date.month == target_month and tr.operation_type == "income":
            total += Decimal(str(tr.operation_amount))

    return total * Decimal("0.8")

    
def get_last_month_expense_statistic() -> tuple:
    log_record = get_operation_history()
    today = datetime.today()

    food_expense = Decimal("0")
    bills_expense = Decimal("0")
    drugs_expense = Decimal("0")
    games_expense = Decimal("0")
    other_expense = Decimal("0")

    if today.month == 1:
        target_month = 12
    else:
        target_month = today.month - 1

    for tr in log_record:
        tr_date = tr.operation_date
        if tr_date.month == target_month and tr.operation_type == "expense":
            if tr.operation_category == 1:
                food_expense += Decimal(str(tr.operation_amount))
            elif tr.operation_category == 2:
                bills_expense += Decimal(str(tr.operation_amount))
            elif tr.operation_category == 3:
                drugs_expense += Decimal(str(tr.operation_amount))
            elif tr.operation_category == 4:
                games_expense += Decimal(str(tr.operation_amount))
            elif tr.operation_category == 5:
                other_expense += Decimal(str(tr.operation_amount))
    
    total_expense = food_expense + bills_expense + drugs_expense + games_expense + other_expense

    return (food_expense, bills_expense, drugs_expense, games_expense, other_expense, total_expense)