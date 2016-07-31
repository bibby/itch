import logging
import os

log_level = logging.WARNING
env_level = os.environ.get('LOG_LEVEL', None)
if env_level:
    if not isinstance(env_level, int):
        level = getattr(logging, env_level)
        if isinstance(log_level, int):
            log_level = level

logging.basicConfig(
    level=log_level,
    format='%(asctime)s %(levelname)s:%(name)s: %(message)s'
)
logger = logging.getLogger("twitch_api")
logger.debug("Log Level: %d", log_level)
