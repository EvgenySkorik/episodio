class AppError(Exception):
    """Базовое исключение приложения."""

class UserNotFoundError(AppError):
    """Ошибка пользователь не найден"""

class MovieNotFoundError(AppError):
    """Ошибка фильм/сериал не найден"""

class KinopoiskAPIError(AppError):
    """Ошибка при запросе к Кинопоиску."""


class NotificationError(AppError):
    """Ошибка при отправке уведомления."""


class SeriesUpdateError(AppError):
    """Ошибка при проверке обновлений сериала."""

class SecurityError(Exception):
    """Базовая ошибка безопасности."""

class TokenExpiredError(SecurityError):
    """Токен истёк."""

class InvalidTokenError(SecurityError):
    """Токен невалиден."""

class FileOperationError(AppError):
    """Ошибка при работе с файлами"""

class LogFileNotFoundError(FileOperationError):
    """Файл логов не найден"""

class LogFileReadError(FileOperationError):
    """Ошибка чтения файла логов"""

class TestError(AppError):
    """Ошибка для теста Hawk"""
