from constants import USER_MESSAGES

def get_msg_success_logged(operation_type="неизвестно"):
    """Возвращает сообщение об успешной записи с типом операции."""
    return USER_MESSAGES["MSG_SUCCESS_LOGGED"].format(operation_type=operation_type)


def get_msg_exit():
    """Возвращает сообщение о завершении программы."""
    return USER_MESSAGES["MSG_EXIT"]


def get_msg_transaction_cancelled():
    """Возвращает сообщение об отмене операции."""
    return USER_MESSAGES["MSG_CANCELLED"]


def get_err_invalid_input(detail=""):
    """Возвращает сообщение об ошибке ввода с опциональной деталью."""
    return USER_MESSAGES["ERR_INVALID_INPUT"].format(detail=detail) if detail else USER_MESSAGES["ERR_INVALID_INPUT"]


def get_err_input_not_a_number():
    """Возвращает сообщение об ошибке ввода: введенное не является числом."""
    return USER_MESSAGES["ERR_INPUT_NOT_A_NUMBER"]


def get_err_zero_amount():
    """Возвращает сообщение об ошибке нулевой суммы."""
    return USER_MESSAGES["ERR_ZERO_AMOUNT"]


def get_err_empty_input():
    """Возвращает сообщение об ошибке пустой строки."""
    return USER_MESSAGES["ERR_EMPTY_INPUT"]


def get_prompt_individual_entrepreneurship():
    """Возвращает запрос про доход от ИП."""
    return USER_MESSAGES["PROMPT_INDIVIDUAL_ENTREPRENEURSHIP"]


def get_prompt_transaction_type():
    """Возвращает запрос типа операции."""
    return USER_MESSAGES["PROMPT_TRANSACTION_TYPE"]


def get_prompt_amount():
    """Возвращает запрос суммы транзакции."""
    return USER_MESSAGES["PROMPT_AMOUNT"]


def get_prompt_comment():
    """Возвращает запрос комментария."""
    return USER_MESSAGES["PROMPT_COMMENT"]


def get_prompt_transaction_category():
    """Возвращает запрос категории с динамическим списком опций."""
    return USER_MESSAGES["PROMPT_TRANSACTION_CATEGORY"]


def get_prompt_menu(commands="add (добавить расход/доход), balance (ВРЕМЕННО НЕ РАБОТАЕТ), exit (выйти)"):
    """Возвращает главное меню с динамическим списком команд."""
    return USER_MESSAGES["PROMPT_MENU"].format(commands=commands)