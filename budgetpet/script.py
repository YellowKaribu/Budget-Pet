import json
from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.sql import insert

# Настройки подключения к базе
engine = create_engine('mysql+pymysql://admin:contract@localhost/budget', echo=True)

# Имя таблицы
table_name = 'operations_history'

# Загружаем таблицу через метаданные
metadata = MetaData()
metadata.reflect(bind=engine)
table = metadata.tables[table_name]

# Путь к JSONL
jsonl_path = 'transactions.jsonl'

with engine.connect() as conn:
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)

            # Нормализуем timestamp
            try:
                ts = datetime.strptime(data['timestamp'], '%d-%m-%Y %H:%M:%S')
            except ValueError:
                print(f"❌ Невалидная дата: {data['timestamp']}")
                continue

            # Приводим типы
            data['timestamp'] = ts
            data['amount'] = float(data['amount']) if isinstance(data['amount'], str) else data['amount']
            data['category'] = int(data['category']) if data['category'] not in (None, "") else None

            # Подгоняем под структуру таблицы
            row = {
                'id': data['id'],
                'timestamp': data['timestamp'],
                'type': data['type'],
                'amount': data['amount'],
                'comment': data['comment'],
                'category': data.get('category'),
                'tax_status': data.get('tax_status')
            }

            try:
                conn.execute(insert(table).values(**row))
            except Exception as e:
                print(f"❌ Ошибка вставки ID {data['id']}: {e}")
