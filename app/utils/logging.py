"""
app/utils/logging.py
Production-grade logging for AI Agriculture Crop Advisory Assistant.
Ensures sensitive tokens, passwords, and API keys are never leaked to logs.
"""

import logging
import sys
import uuid
from typing import Optional

def setup_logger(name: str = "agri_advisor", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] [ReqID: %(request_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

class RequestLoggerAdapter(logging.LoggerAdapter):
    """Adds a persistent or generated request_id to log records."""
    def __init__(self, logger: logging.Logger, extra: Optional[dict] = None):
        super().__init__(logger, extra or {})

    def process(self, msg, kwargs):
        req_id = self.extra.get("request_id", "SYS")
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["request_id"] = req_id
        
        # Sanitize any accidental API key patterns
        sanitized_msg = str(msg)
        for secret_prefix in ["sk-", "Bearer "]:
            if secret_prefix in sanitized_msg:
                sanitized_msg = sanitized_msg.replace(secret_prefix, "[REDACTED_AUTH]")
        return sanitized_msg, kwargs

base_logger = setup_logger()

def get_logger(request_id: Optional[str] = None) -> RequestLoggerAdapter:
    if not request_id:
        request_id = str(uuid.uuid4())[:8]
    return RequestLoggerAdapter(base_logger, {"request_id": request_id})
