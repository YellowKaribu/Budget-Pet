from datetime import datetime

def valitate_new_operation_input(user_input) -> tuple[bool, str | None]:
    #fields validation    
    required_fields = {'operation_date', 'type', 'tax_status', 'category', 'amount', 'comment'}
    if not isinstance(user_input, dict):
        return False, "Неверный формат данных: ожидается JSON-объект"
    missing = required_fields - user_input.keys()
    if missing:
        return False, f"Отсутствуют поля: {', '.join(missing)}"
    
    #date validation
    date_str = user_input.get('operation_date')
    if date_str in (None, '', 'null'):
        user_input['operation_date'] = None
    else:
        if not isinstance(date_str, str):
            return False, "Дата должна быть строкой в формате YYYY-MM-DD"
        try:
            operation_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "Неверный формат даты. Ожидается YYYY-MM-DD"
        if operation_date > datetime.today().date():
            return False, "Путешествия во времени еще не изобрели. Дата не может быть в будущем."
        user_input['operation_date'] = operation_date.isoformat()

    
    #type validation
    if user_input['type'] not in ['income', 'expense']:
        return False, "Поле 'type' должно быть 'income' или 'expense'"
    
    #amount validation
    try:
        amount = float(user_input['amount'])
    except (ValueError, TypeError):
        return False, "Сумма должна быть числом."
    if amount == 0:
        return False, "Сумма не может быть 0."
    
    return True, None