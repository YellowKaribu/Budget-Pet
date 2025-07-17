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
        {"timestamp": f"{prev_year}-{prev_month:02d}-01 10:00:00", "amount": "100.50"},
        {"timestamp": f"{prev_year}-{prev_month:02d}-15 12:30:00", "amount": "200.00"},
        {"timestamp": f"{today.year}-{today.month:02d}-01 09:00:00", "amount": "999.00"},  # не попадёт
    ]

    # Подменим функцию get_transaction_log
    def mock_get_transaction_log():
        return fake_log

    monkeypatch.setattr("application.get_transaction_log", mock_get_transaction_log)

    # Выполняем тест
    result = calculate_last_month_income()
    assert Decimal(result) == Decimal("300.50")


import pytest
from decimal import Decimal
from datetime import datetime
from application import monthly_recalculations

def test_monthly_recalculations(monkeypatch):
    today = datetime.now().strftime("%Y-%m-%d")

    # Фейковое мета-хранилище
    fake_meta = {}

    # Фейковое состояние баланса
    @dataclass
    class FakeBalance:
        rent: str
        available_funds: str
        reserve: str
    
    # Моки
    monkeypatch.setattr("application.get_meta_data", lambda path: fake_meta.copy())
    monkeypatch.setattr("application.save_meta_data", lambda path, data: fake_meta.update(data))
    monkeypatch.setattr("application.get_state", lambda: FakeBalance(
    rent="500", available_funds="1000", reserve="300"
))
    monkeypatch.setattr("application.calculate_last_month_income", lambda: "200")
    
    # Захват обновлённого состояния
    captured_state = {}
    def fake_save_state(state):
        captured_state["rent"] = state.rent
        captured_state["available_funds"] = state.available_funds
        captured_state["reserve"] = state.reserve
    monkeypatch.setattr("application.save_state", fake_save_state)

    # Вызов
    monthly_recalculations()

    # Проверки
    assert fake_meta["last_monthly_recalculations"] == today
    assert captured_state["rent"] == "810"
    assert captured_state["available_funds"] == str(Decimal("1000") + Decimal("200"))
    assert captured_state["reserve"] == str(Decimal("300") - Decimal("200"))
