import pytest
from decimal import Decimal
from datetime import datetime
from application import calculate_last_month_income, get_transaction_log
from dataclasses import dataclass

def test_calculate_last_month_income(monkeypatch):
    today = datetime.today()
    
    # Определим прошлый месяц и год
    if today.month == 1:
        prev_month = 12
        prev_year = today.year - 1
    else:
        prev_month = today.month - 1
        prev_year = today.year

    # Подготовим фейковые транзакции
    fake_log = [
        {"id": 1, "timestamp": "13-06-2025 17:48:03", "type": "income", "amount": "100", "comment": "\u0442\u0435\u0441\u0442", "category": 1, "tax_status": "\u0434\u0430"},
        {"id": 1, "timestamp": "01-06-2025 17:48:03", "type": "expense", "amount": 200, "comment": "food","category": 1, "tax_status": 1},
        {"id": 2, "timestamp": "01-07-2025 17:48:03", "type": "expense", "amount": 1700, "comment": "20 простуда, 50 антибиотик","category": 3, "tax_status": 1}
        ]

    # Подменим функцию get_transaction_log
    def mock_get_transaction_log():
        return fake_log

    monkeypatch.setattr("application.get_transaction_log", mock_get_transaction_log)

    # Выполняем тест
    result = calculate_last_month_income()
    assert Decimal(result) == Decimal("100")
