from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from functools import lru_cache




@lru_cache
def get_logger(module_name, folder, fname):
    logger = logging.getLogger(module_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    path_to = f"logs/{folder}"
    Path(path_to).mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(f"{path_to}/{datetime.now():%Y-%m-%d}-{fname}.log")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    return logger


@lru_cache
def get_timed_logger(module_name, folder, fname):
    logger = logging.getLogger(module_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    path_to = f"logs/{folder}"
    Path(path_to).mkdir(parents=True, exist_ok=True)
    fh = TimedRotatingFileHandler(f"{path_to}/{fname}.log", when="h", interval=24)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    return logger
