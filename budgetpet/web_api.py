import os
from budgetpet.logger import logger
from decimal import Decimal
from flask import Flask, jsonify, render_template, request, url_for, redirect
from budgetpet.infrastructure import get_current_budget_state, get_operation_history, save_budget_state
from budgetpet.application import process_new_operation, should_run_monthly_event
from budgetpet.validators import valitate_new_operation_input
from typing import Any
from budgetpet.models import LoggingError
from budgetpet.db import db_cursor
from budgetpet.models import BudgetState


app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../web/templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../web/static'),
    static_url_path='/static'
)

@app.route('/balance')
def balance_page():
    return render_template('balance.html')

@app.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.get_json()
    required_fields = ['reserve', 'available_funds', 'rent', 'taxes']

    if not data or any(field not in data for field in required_fields):
        return jsonify({'error': 'Missing fields'}), 400
    
    try:
        state = BudgetState(
            reserve=Decimal(str(data['reserve'])),
            available_funds=Decimal(str(data['available_funds'])),
            rent=Decimal(str(data['rent'])),
            taxes=Decimal(str(data['taxes']))
        )

    except (ValueError, TypeError):
        logger.error("Ошибка при получении данных нового баланса")
        return jsonify({'error': 'Invalid data format'}), 400
    
    try:
        with db_cursor() as cursor:
            save_budget_state(state, cursor)

    except Exception as e:
        logger.error("Ошибка при сохранении нового баланса в бд: %s", e)
        return jsonify({'Error': 'Update failed', 'details': str(e)}), 500
    
    return jsonify({'status': 'success'})


@app.route('/budget_state.json')
def budget_state_json():
    with db_cursor() as cursor:
        state = get_current_budget_state(cursor)
        data = state.model_dump()

        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)

        return jsonify(data)


@app.route('/transactions.jsonl')
def transactions_json():
    operations_history = get_operation_history()
    data = [record.model_dump() for record in operations_history]
    return jsonify(data)


@app.route('/transactions_log')
def transactions_log():
    operations_history = get_operation_history()
    return render_template("transactions_log.html", transactions=operations_history)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/add_transaction')
def balance():
    return render_template('add_transaction.html')


@app.route('/new_operation.json', methods=['POST'])
def new_operation():
    user_data: Any = request.json
    logger.debug('АПИ принимает запрос на новую операцию со следующими данными: %s', user_data)

    if not isinstance(user_data, dict):
        return jsonify({"error": "Неверный формат данных"}), 400

    is_valid, error_message = valitate_new_operation_input(user_data)
    if not is_valid:
        return jsonify({"error": error_message}), 400

    try:
        process_new_operation(user_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except LoggingError as e:
        return jsonify({"error": "Ошибка логирования операции"}), 500
    except Exception:
        logger.exception("Внутренняя ошибка сервера при обработке операции")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500
    
    return jsonify({'ok': True})


@app.route('/statistics')
def statistics():
    return render_template('statistics.html')



if __name__ == '__main__':
    should_run_monthly_event()
    app.run(debug=True)