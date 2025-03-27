import logging
from datetime import datetime


class LogHandler:
    @staticmethod
    def get_logger(str_module_name):
        logger = logging.getLogger(str_module_name)
        logger.setLevel(logging.DEBUG)

        date_time = datetime.now()
        date_time.strftime("%d-%m-%Y : %I:%M:%S %p").__str__()

        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('{:%Y-%m-%d_%I%p-%M-%S}.log'.format(datetime.now()))
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.DEBUG)

        c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        return logger
