import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def log_api_request(
    service_name: str,
    endpoint: str,
    request_data: Dict[str, Any],
    response_data: Dict[str, Any]
) -> None:
    """Log API request details"""
    logger.info(f"[{service_name}] {endpoint} - Request: {request_data}, Response: {response_data}")