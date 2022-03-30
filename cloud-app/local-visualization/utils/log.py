import logging

from colorlog import ColoredFormatter

"""
# Change log

Date: 02 Dec 2021: 
    - Disabled colored log Feature
    - Disabled logging into logfile to avoid disk space full problem 
"""

def setup_logger():
#def setup_logger(mainlog_fname='main.log', errlog_fname='error.log'):
    """Setup application logging.

    Args:
        mainlog_fname - name of the file to log normal level messages
        errlog_fname - name of the file to log errors
    """
    log_format = '%(asctime)s: %(levelname)s - %(module)s:%(lineno)d - %(message)s'
    formatter = logging.Formatter(log_format)
    datefmt = "[%Y-%m-%d %H:%M:%S]"

    color_format = ColoredFormatter(
        "%(asctime)s: %(log_color)s %(levelname) - 2s%(reset)s - %(module)s:%(lineno)d - %(message)s",
        datefmt=datefmt,
        reset=False,
        log_colors={'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red', })

    # Save full log
    #logging.basicConfig(level=logging.DEBUG, datefmt=datefmt,format=log_format,filename=mainlog_fname,filemode="w")
    logging.basicConfig(level=logging.DEBUG, datefmt=datefmt,format=log_format)

    logger = logging.getLogger()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(color_format)
    #logger.addHandler(console_handler)

    #error_handler = logging.FileHandler(errlog_fname)
    #error_handler.setLevel(logging.ERROR)
    #error_handler.setFormatter(formatter)
    #logger.addHandler(error_handler)

    # disable log messages from asyncio library
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    return logger


def update_logger_verbose_level(logger, verbose_level):
    if verbose_level == '1':
        #logger.handlers[1].setLevel(logging.WARN)
        logger.setLevel(logging.WARN)
        logger.info("Enabled Warning Mode ".format(verbose_level))
    elif verbose_level == '2':
        #logger.handlers[1].setLevel(logging.DEBUG) 
        logger.setLevel(logging.DEBUG)
        logger.info("Enabled Debug Mode".format(verbose_level))
    else:
        #logger.handlers[1].setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.info("Enabled Info Mode".format(verbose_level))


def update_logger_verbose_level_from_config_file(logger, config_file_obj):
    if config_file_obj["troubleshoot"]:
        if config_file_obj["troubleshoot"]["enable_debug_mode"] is True:
          verbose_level = '2'
        else:
            verbose_level = 'INFO' 
    update_logger_verbose_level(logger, verbose_level)