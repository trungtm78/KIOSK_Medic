from ..servicelogs.servicelogger import logger


class MetricsService:
    def bump(self, key: str) -> None:
        logger.debug(f"METRIC bump: {key}")

    def mark_session_start(self) -> None:
        logger.debug("METRIC: session_start")

    def mark_session_end(self) -> None:
        logger.debug("METRIC: session_end")

