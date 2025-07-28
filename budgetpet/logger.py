import logging

logger = logging.getLogger("budgetpet")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.FileHandler("debug.log", mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
