import os
from budgetpet.domain.models import OperationDTO, Operation
from flask import Flask, jsonify, render_template, request
from pydantic import ValidationError


def create_app(services: dict) -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), '../../web/templates'),
        static_folder=os.path.join(os.path.dirname(__file__), '../../web/static'),
        static_url_path='/static'
    )

    app.config['services'] = services

    @app.route('/')
    def home():
        return render_template('index.html')


    @app.route('/balance')
    def balance_page():
        return render_template('balance.html')
    

    @app.route('/add_transaction')
    def add_transaction():
        return render_template('add_transaction.html')
    

    @app.route('/statistics')
    def statistic_page():
        return render_template('statistics.html')


    @app.route('/operations-history')
    def operations_log():
        return render_template('operations-history.html')


    @app.route('/delete_operation/<int:operation_id>', methods=["POST"])
    def delete_operation(operation_id):
        try:
            operation_service = app.config['services']['operations']
            operation_service.delete_operation(operation_id)
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500
    


    @app.route('/budget_state.json')
    def budget_state_json():
        try:
            budget_service = app.config['services']['budget']
            balance = budget_service.get_budget_state()
            return jsonify({'balance': balance.model_dump(mode='json')})
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @app.route('/update_balance', methods=['POST'])
    def update_balance():
        data = request.get_json()
        try:
            budget_service = app.config['services']['budget']
            budget_service.save_budget_state(data)
            return jsonify({'status': 'success'})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            budget_service.logger.error(f"Error updating balance: {e}")
            return jsonify({'error': 'Update failed', 'details': str(e)}), 500


    def serialize_for_frontend(op: Operation):
        return {
            "id": op.id,
            "operation_date": op.date.isoformat(),
            "operation_type": op.type,
            "operation_amount": op.amount,
            "operation_category": op.category,
            "operation_tax_status": float(op.tax_rate) if op.tax_rate else None,
            "operation_comment": op.comment
        }


    @app.route('/transactions.jsonl')
    def transactions_json():
        try:
            operations_service = app.config['services']['operations']
            operations_history = operations_service.get_operations_history()
            data = [serialize_for_frontend(record) for record in operations_history]

            return jsonify(data)
        except Exception as e:
            operations_service.logger.error(f"Error fetching transactions: {e}")
            return jsonify({'error': 'Failed to fetch transactions'}), 500


    @app.route('/transactions_log')
    def transactions_log():
        try:
            operations_service = app.config['services']['operations']
            operations_history = operations_service.get_operation_history()
            return render_template("transactions_log.html", transactions=operations_history)
        except Exception as e:
            operations_service.logger.error(f"Error rendering transactions log: {e}")
            return render_template("error.html", error=str(e)), 500


    @app.route('/new_operation.json', methods=['POST'])
    def new_operation():
        json_data = request.get_json()
        if json_data is None:
            return jsonify({'error': 'No JSON data provided'}), 400
        try:
            operation_dto = OperationDTO(**json_data)
        except ValidationError as e:
            messages = [err['msg'] for err in e.errors()]
            return jsonify({'error': messages[0]}), 422

        
        try:
            operation = operation_dto.to_domain()
        except ValidationError as e:
            messages = [err['msg'] for err in e.errors()]
            return jsonify({'error': messages[0]}), 422

        
        try:
            operation_service = app.config['services']['operations']
            operation_service.add_operation(operation)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': f'Error adding operation: {str(e)}'}), 500

    return app