from datetime import datetime


class Log:
    @classmethod
    def info(cls, message):
        cls._log('INFO', message)

    @classmethod
    def error(cls, message):
        cls._log('ERROR', message)

    @classmethod
    def debug(cls, message):
        cls._log('DEBUG', message)

    @staticmethod
    def _log(level, message):
        current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        message = '{time} - {level} {message}'.format(time=current_date, level=level, message=message)
        print(message)