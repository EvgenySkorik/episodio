import logging


logging.basicConfig(
    level=logging.INFO,
    filename="KinoMovieApi.log",
    filemode="a",
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    encoding="utf-8",
    force=True,
)


def get_logger(name=None):
    """Возвращает настроенный логгер"""
    logger = logging.getLogger(name or __name__)

    return logger
