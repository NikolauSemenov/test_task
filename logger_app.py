import os
import logging
from logging.handlers import TimedRotatingFileHandler

FOLDER_LOG = "log"
LOGGING_CONFIG_FILE = 'loggers.log'


class LoggingMain:
    """
    Настройка логирования
    """
    def __init__(self,
                 path_file=LOGGING_CONFIG_FILE,
                 folder=FOLDER_LOG,
                 formatter=logging.Formatter('%(asctime)s  %(name)s %(funcName)s %(levelname)s: %(message)s'),
                 level=logging.DEBUG):

        self.path_file = path_file
        self.formatter = formatter
        self.level = level
        self.folder = folder

    def create_log(self):
        """
        Создает папку с файлом
        для хранения лога
        :return:
        """
        os.makedirs(os.path.dirname(os.path.join(self.folder, self.path_file)), exist_ok=True)
        file_handler = TimedRotatingFileHandler(os.path.join(self.folder, self.path_file), when='midnight')
        file_handler.setFormatter(self.formatter)
        return file_handler

    def get_logging(self, log_name: str):
        """
        :return:
        """
        logger = logging.getLogger(log_name)
        logger.setLevel(self.level)
        logger.addHandler(self.create_log())
        return logger


