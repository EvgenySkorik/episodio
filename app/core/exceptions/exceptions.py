class AppError(Exception):
    """Базовое исключение приложения."""
    pass

class UserNotFoundError(AppError):
    """Ошибка пользователь не найден"""
    pass

class MovieNotFoundError(AppError):
    """Ошибка фильм/сериал не найден"""
    pass

class KinopoiskAPIError(AppError):
    """Ошибка при запросе к Кинопоиску."""
    pass


class NotificationError(AppError):
    """Ошибка при отправке уведомления."""
    pass


class SeriesUpdateError(AppError):
    """Ошибка при проверке обновлений сериала."""
    pass

class SecurityError(Exception):
    """Базовая ошибка безопасности."""
    pass

class TokenExpiredError(SecurityError):
    """Токен истёк."""
    pass

class InvalidTokenError(SecurityError):
    """Токен невалиден."""
    pass

class FileOperationError(AppError):
    """Ошибка при работе с файлами"""
    pass

class LogFileNotFoundError(FileOperationError):
    """Файл логов не найден"""
    pass

class LogFileReadError(FileOperationError):
    """Ошибка чтения файла логов"""
    pass