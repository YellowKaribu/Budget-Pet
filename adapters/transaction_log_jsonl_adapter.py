import json
from ports.output_port import TransactionsLogPort
from config.config import TRANSACTIONS_LOG_PATH

class TransactionsLoggerJsonl(TransactionsLogPort):
    def get_transaction_log(self) -> list[dict]:
        with open(TRANSACTIONS_LOG_PATH, "r") as f:
            lines = f.readlines()
            entries = [json.loads(line) for line in lines if line.strip()]
            return entries
        
    def write_transaction_log(self, entry: dict) -> None:
        with open(TRANSACTIONS_LOG_PATH, "a") as f:
            json.dump(entry, f)
            f.write("\n")