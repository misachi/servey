import logging
import logging.config

logger = None
if logger is None:
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
    logger = logging.getLogger('serveyError')
