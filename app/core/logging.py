import logging

from app.core.config import settings


def setup_logging():
    """Настройка логирования"""

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

    return logging.getLogger()


def get_logger(name=None):
    """Возвращает настроенный логгер"""
    logger = logging.getLogger(name or __name__)

    return logger
