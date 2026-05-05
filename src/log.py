import logging
from collections.abc import MutableMapping
from typing import Any, cast

import structlog
from structlog.processors import CallsiteParameter, CallsiteParameterAdder
from structlog.types import Processor

from src.constants import LOG_FILE


def init_logger() -> None:
    def fbl(
        logger: logging.Logger,
        _method_name: str,
        event_dict: MutableMapping[str, Any],
    ) -> MutableMapping[str, Any]:
        if logger is None:
            return event_dict
        if getattr(logger, "disabled", False):
            raise structlog.DropEvent
        level = event_dict.get("level")
        if level is None:
            return event_dict
        if isinstance(level, str):
            level = logging.getLevelName(level.upper())
        if isinstance(level, str) and level.isdigit():
            level = int(level)
        if isinstance(level, int) and level < logger.getEffectiveLevel():
            raise structlog.DropEvent
        return event_dict

    fbl_processor: Processor = cast(Processor, fbl)

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    structlog.configure(
        processors=[
            fbl_processor,
            CallsiteParameterAdder(
                [
                    CallsiteParameter.FILENAME,
                    CallsiteParameter.LINENO,
                    CallsiteParameter.FUNC_NAME,
                ]
            ),
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            fbl_processor,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        ],
        processor=structlog.processors.JSONRenderer(),
    )

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(formatter)
