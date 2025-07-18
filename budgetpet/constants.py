USER_MESSAGES = {
    "MSG_SUCCESS_LOGGED": "Операция успешно записана.",
    "MSG_EXIT": "Программа завершена. До свидания!",
    "MSG_CANCELLED": "Операция отменена. Возврат в меню.",
    "ERR_INVALID_INPUT": "Неверный ввод данных.",
    "ERR_ZERO_AMOUNT": "Сумма не может быть нулевой.",
    "ERR_EMPTY_INPUT": "Ошибка: пустой ввод.",
    "ERR_INPUT_NOT_A_NUMBER":"Пожалуйста, введите число.",
    "PROMPT_INDIVIDUAL_ENTREPRENEURSHIP": "Доход от ИП? Да/нет: ",      
    "PROMPT_TRANSACTION_TYPE": "Чтобы отменить транзакцию, введите 'отмена' в любой момент\n"\
        "Введите + для дохода, - для расхода: ",
    "PROMPT_AMOUNT": "Введите сумму транзакции: ",
    "PROMPT_COMMENT": "Введите комментарий к операции: ",
    "PROMPT_TRANSACTION_CATEGORY": "Выберите категорию расхода.\n"
        "1 - еда \n"\
        "2 - коммуналка \n"\
        "3 - лекарства \n "\
        "4 - развлечения \n"\
        "5 - прочее: ",  
    "PROMPT_MENU": "Добро пожаловать в финансовый трекер личных расходов.\n"\
        "Введите: add (добавить расход/доход), exit (выйти): "
}
EXPENSE_CATEGORY = {
    "1": "Еда",
    "2": "Коммуналка",
    "3": "Лекарства",
    "4": "Развлечения",
    "5": "Прочее"
    }
BUDGET_PATH = "budget_state.json"
TRANSACTIONS_LOG_PATH = "transactions.jsonl"
META_PATH = "meta.json"
