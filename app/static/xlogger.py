import logging
from sys import stdout as display

# Make your own log styles here
FORMAT_DISPLAY = '%(levelname) -7s - %(message)s'
FORMAT_LOG_FILE = '%(asctime)s | %(name)s | %(levelname) -7s - %(message)s'
FORMAT_DATETIME = '%Y/%m/%d %H:%M:%S'
BASE_LOG_LEVEL = logging.DEBUG
DISPLAY_LEVEL = logging.DEBUG
FILE_LEVEL = logging.INFO
FILE_OUTPUT = 'output.log'


class ColorFormatter(logging.Formatter):
    """Logging Formatter to add colors."""
    # Define Colors
    NO_COLOR = "\x1b[m"
    BLACK, RED, GREEN, ORANGE, BLUE, PURPLE, L_BLUE, GREY, WHITE = \
        map("\x1b[%dm".__mod__, range(30, 39))
    R_BLACK, R_RED, R_GREEN, R_ORANGE, R_BLUE, R_PURPLE, R_L_BLUE, R_GREY, R_WHITE = \
        map("\x1b[%d;47m".__mod__, range(30, 39))
    BOLD_RED = '\x1b[31;1m'
    R_BOLD_RED = '\x1b[30;41m'

    # Define format for color display
    format = FORMAT_DISPLAY
    FORMATS = {
        logging.DEBUG: BLUE + format + NO_COLOR,
        logging.INFO: WHITE + format + NO_COLOR,
        logging.WARNING: ORANGE + format + NO_COLOR,
        logging.ERROR: RED + format + NO_COLOR,
        logging.CRITICAL: BOLD_RED + format + NO_COLOR
    }

    def format(self, record):
        # Use colorized format replacing originals.
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_my_logger(mod_name):
    """init a logger, with both display and file output"""
    logger = logging.getLogger(mod_name)
    logger.setLevel(BASE_LOG_LEVEL)
    formatter_file = logging.Formatter(fmt=FORMAT_LOG_FILE, datefmt=FORMAT_DATETIME)

    # StreamHandler
    stream_handler = logging.StreamHandler(display)
    stream_handler.setLevel(DISPLAY_LEVEL)
    stream_handler.setFormatter(ColorFormatter())  # Colorize 'Formatter' for display
    logger.addHandler(stream_handler)

    # FileHandler
    file_handler = logging.FileHandler(FILE_OUTPUT, encoding='utf-8')
    file_handler.setLevel(FILE_LEVEL)
    file_handler.setFormatter(formatter_file)
    logger.addHandler(file_handler)

    # Other Handlers
    # ...

    return logger
