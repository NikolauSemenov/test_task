import logging


class LoggingMain:
    """
    Настройка логирования
    """
    def __init__(self,
                 formatter=logging.Formatter('%(asctime)s  %(name)s %(funcName)s %(levelname)s: %(message)s'),
                 level=logging.DEBUG):

        self.formatter = formatter
        self.level = level

    def get_logging(self, log_name: str):
        """
        :return:
        """
        logger = logging.getLogger(log_name)
        logger.setLevel(self.level)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(self.formatter)
        logger.addHandler(consoleHandler)

        return logger


