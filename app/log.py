import logging
import sys
from pathlib import Path

from loguru import logger

from app.config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # type: ignore
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    try:
        logging.root.setLevel(settings.log_level)
    except ValueError:
        sys.exit(f"Set appropriate 'LOG_LEVEL' environment variable. current {settings.LEVEL=}")

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    if settings.JSON_LOG:
        logger_config = dict(sink=sys.stdout, serialize=settings.JSON_LOG, format="{message}")
    else:
        # logger_config = dict(sink=sys.stdout)
        logger_config = dict(sink=sys.stdout, format=settings.LOGURU_FORMAT)
    logger.configure(handlers=[logger_config], extra={"request_id": ''})  # extra[request_id] 기본값 지정
    if settings.SAVE:
        log_save_path = Path(settings.LOG_SAVE_PATH) / "{time:YYYY}" / "{time:MM}" / "{time:YYYYMMDD}_info.log"
        logger.add(  # type: ignore
            log_save_path,
            level=settings.log_level,
            rotation=settings.ROTATION,
            retention=settings.RETENTION,
            compression=settings.COMPRESSION,
            serialize=settings.JSON_LOG,
            format=settings.LOGURU_FORMAT
        )
    return logger.bind()


class Log:
    """todo : 펑션으로 처리"""
    TRACE: int = 10
    log_level = int(settings.log_level)

    @staticmethod
    def is_trace_enable():
        return Log.log_level <= Log.TRACE

    @staticmethod
    def is_debug_enable():
        return Log.log_level <= logging.DEBUG

    @staticmethod
    def is_info_enable():
        return Log.log_level <= logging.INFO

    @staticmethod
    def is_warn_enable():
        return Log.log_level <= logging.WARN

    @staticmethod
    def is_error_enable():
        return Log.log_level <= logging.ERROR

    @staticmethod
    def is_fatal_enable():
        return Log.log_level <= logging.FATAL
