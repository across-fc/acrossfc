import logging

LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d [%(levelname)s] %(filename)s:%(lineno)d: %(message)s"
)
logging.basicConfig(
    level=logging.WARNING, format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"
)
