import logging
import os
import datetime

parent_dir = 'logs'

def get_logger(log_name, filename=None, debugmode=False):
    if filename is None:
        filename = 'log_' + str(log_name) + '_' + str(datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M')) + '.log'
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s module:%(module)s function:%(module)s : %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s -- %(message)s')

    file_location = os.path.join(parent_dir, filename)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    file_handler = logging.FileHandler(file_location)
    if debugmode:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.WARN)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    if debugmode:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger = logging.getLogger(log_name)

    logger.addHandler(file_handler)
    logger.propagate = False
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

    return logger
