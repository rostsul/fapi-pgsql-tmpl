import logging

import structlog
from structlog.processors import JSONRenderer, TimeStamper, add_log_level

from app.config import settings


def setup_logging():
    shared_processors = [
        TimeStamper(fmt="iso", utc=True),
        add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=[*shared_processors, JSONRenderer()],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=JSONRenderer(),
        foreign_pre_chain=[TimeStamper(fmt="iso", utc=True), add_log_level],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.LOG_LEVEL.upper())
