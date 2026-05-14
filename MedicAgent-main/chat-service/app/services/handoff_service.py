from ..servicelogs.servicelogger import logger


class HandoffService:
    def open_channel(self) -> None:
        logger.info("HANDOFF: open channel")

    def close_channel(self) -> None:
        logger.info("HANDOFF: close channel")

