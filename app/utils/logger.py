import logging

logger=logging.getLogger("THRESHOLD")
logger.setLevel(logging.INFO)
file_handler=logging.FileHandler("threshold.log")
formatter=logging.Formatter("%(asctime)s: %(levelname)s : %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
