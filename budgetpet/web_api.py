import os
from budgetpet.logger import logger
from decimal import Decimal
from flask import Flask, jsonify, render_template, request, url_for, redirect
from budgetpet.constants import BUDGET_PATH, TRANSACTIONS_LOG_PATH
from budgetpet.infrastructure import get_current_budget_state, get_operation_history
from dataclasses import asdict
from budgetpet.application import process_new_operation, should_run_monthly_event
from budgetpet.validators import valitate_new_operation_input
from typing import Any
from budgetpet.models import LoggingError

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../web/templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../web/static'),
    static_url_path='/static'
)

@app.route('/balance')
def balance_page():
    return render_template('balance.html')


@app.route('/budget_state.json')
def budget_state_json():
    state = get_current_budget_state()
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


from typing import Any
from flask import request, jsonify

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


should_run_monthly_event()


if __name__ == '__main__':
    app.run(debug=True)