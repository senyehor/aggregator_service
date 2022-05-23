import logging

from aggregator.services import get_module_dir


class ColoredFormatter(logging.Formatter):

    def format(self, record):
        formatter = logging.Formatter(fmt="%(levelname)s - %(asctime)s - %(message)s", datefmt="%m-%d %H:%M:%S")  # noqa
        return formatter.format(record)


level = logging.DEBUG

logger = logging.getLogger(__name__)
logger.setLevel(level)
formatter = ColoredFormatter()

handlers: list[logging.Handler] = [
    logging.FileHandler(get_module_dir().joinpath(".log")),
    logging.StreamHandler()
]
if not logger.handlers:
    for handler in handlers:
        handler.setLevel(level)
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)
