import logging
from logging import handlers
from logging.handlers import RotatingFileHandler
from enum import Enum
import sys
from AnsiColors import Colors, Color, Weight
    
class LogFormatter(logging.Formatter):

    defaultFormat = "%(asctime)s [%(module)s] %(filename)s:%(lineno)d %(levelname)s: %(message)s"
    colors = Colors()
    _debugColor = colors(Color.Grey)
    _infoColor = _debugColor
    _warningColor = colors(Color.Yellow)
    _errorColor = colors(Color.Red)
    _criticalColor = colors(Color.Red, weight=Weight.Bold)
    _formats = {
        logging.DEBUG: _debugColor + defaultFormat + Colors.Reset,
        logging.INFO: _infoColor + defaultFormat + Colors.Reset,
        logging.WARNING: _warningColor + defaultFormat + Colors.Reset,
        logging.CRITICAL: _criticalColor + defaultFormat + Colors.Reset,
        logging.ERROR: _errorColor + defaultFormat + Colors.Reset
    }

    def format(self, record):
        log_fmt = self._formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(console_handler)
    logFormatter = LogFormatter()
    console_handler.setFormatter(logFormatter)
    logger.debug("log debug")
    logger.info("log info")
    logger.warning("log warning")
    logger.error("log error")
    logger.critical("log critical")
    logger.fatal("log fatal")
    try:
        x = 2  / 0
    except:
        logger.exception("log exception")
        
