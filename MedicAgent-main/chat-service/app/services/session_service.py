from ..servicelogs.servicelogger import logger


class SessionService:
    def init(self) -> None:
        logger.debug("SESSION: init")

    def close(self) -> None:
        logger.debug("SESSION: close")

