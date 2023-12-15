import logging


class CustomFormatterConsole(logging.Formatter):
    """Logging filter to Console handler"""

    white_blue = "\x1b[38;5;75m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    back_grey = "\x1b[38;5;7m"
    cyan = "\x1b[38;5;14m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] - [%(name)s] - [%(levelname)s] - [pathname: %(pathname)s] - [function: %(funcName)s] - [line: %(lineno)d]\n\t%(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    FORMATS = {
        logging.DEBUG: cyan + format + reset,
        logging.INFO: white_blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + back_grey + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.date_format)
        return formatter.format(record)


class CustomFormatterFile(logging.Formatter):
    """Logging filter to File handler"""

    format = "[%(asctime)s] - [%(name)s] - [%(levelname)s] - [function: %(funcName)s] - [%(message)s]"
    date_format = "%Y-%m-%d %H:%M:%S"

    FORMATS = {
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: format,
        logging.ERROR: format,
        logging.CRITICAL: format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.date_format)
        return formatter.format(record)