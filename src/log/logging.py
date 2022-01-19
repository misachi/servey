import logging
import logging.config


logging.config.fileConfig('log/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger('serveyAccess')
