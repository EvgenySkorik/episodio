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