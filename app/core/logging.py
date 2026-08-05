import logging

from hawk_python_sdk import hawk

from app.core.config import settings


def setup_logging():
    """Настройка логирования с отправкой в Hawk, если есть токен hawk"""

    log_path = settings.log_file_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=settings.log_level,
        filename=str(log_path),
        filemode="a",
        format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
        encoding="utf-8",
        force=True,
    )

    if settings.hawk_secret_token:
        hawk_handler = hawk.logging.HawkHandler(token=settings.hawk_secret_token)
        root_logger = logging.getLogger()
        root_logger.addHandler(hawk_handler)

    return logging.getLogger()


def get_logger(name=None):
    """Возвращает настроенный логгер"""
    logger = logging.getLogger(name or __name__)

    return logger
