import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("budgetpet")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = RotatingFileHandler('debug.log', maxBytes=1024*1024, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
