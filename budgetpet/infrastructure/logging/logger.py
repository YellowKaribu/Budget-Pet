import logging
from logging.handlers import RotatingFileHandler
from budgetpet.domain.interfaces import ILogger

logger = logging.getLogger("budgetpet")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = RotatingFileHandler('debug.log', maxBytes=1024*1024, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class AppLogger(ILogger):
    def debug(self, message: str) -> None:
        logger.debug(message)

    def info(self, message: str) -> None:
        logger.info(message)

    def error(self, message: str) -> None:
        logger.error(message)

    def exception(self, message: str) -> None:
        logger.exception(message)

