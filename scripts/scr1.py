def get_logs_file():
    """Отправить файл с логами"""
    with open('../KinoMovieApi.log', 'r') as f:
        file = f.read()
        return file

